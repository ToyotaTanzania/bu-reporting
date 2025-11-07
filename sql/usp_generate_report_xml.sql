DECLARE @UserID INT = NULL;

    IF OBJECT_ID('tempdb..#ColumnStructures') IS NOT NULL DROP TABLE #ColumnStructures;

    IF CURSOR_STATUS('local', 'unit_cursor') >= 0
    BEGIN
        CLOSE unit_cursor;
        DEALLOCATE unit_cursor;
    END;
    
    DECLARE @ReportYear INT;
    DECLARE @ReportMonth INT;
    
    SELECT TOP 1
        @ReportYear = [year],
        @ReportMonth = [month]
    FROM dbo.submission_period;

    DECLARE @currentMonthName NVARCHAR(6), @previousMonthName NVARCHAR(6);
    DECLARE @currentMonthDate DATE = DATEFROMPARTS(@ReportYear, @ReportMonth, 1);
    SET @currentMonthName = FORMAT(@currentMonthDate, 'MMM-yy');
    SET @previousMonthName = FORMAT(DATEADD(MONTH, -1, @currentMonthDate), 'MMM-yy');

    DECLARE @xmlResult XML = '<Results></Results>';
    DECLARE @unitXml XML;
    DECLARE @page1 XML;
    DECLARE @page2 XML;
    DECLARE @performanceXml XML;
    DECLARE @allPerformanceTablesXml XML;
    DECLARE @executionTrackerXml XML;
    DECLARE @overdueActionsXml XML;
    DECLARE @businessUnit NVARCHAR(100);
    DECLARE @now NVARCHAR(100) = CONVERT(NVARCHAR, GETDATE(), 126);

    DECLARE unit_cursor CURSOR FOR
        SELECT DISTINCT alt_name
        FROM dbo.ufn_get_reported_business_units(@ReportYear, @ReportMonth)
        WHERE id IN
        (
            SELECT DISTINCT bu_id
            FROM dbo.user_permissions
            WHERE active = 1 AND (@UserID IS NULL OR user_id = @UserID)
        );

    OPEN unit_cursor;
    FETCH NEXT FROM unit_cursor INTO @businessUnit;

    WHILE @@FETCH_STATUS = 0
    BEGIN
        SET @allPerformanceTablesXml = '';

        SELECT
            DENSE_RANK() OVER(ORDER BY ColumnStructure) AS StructureId,
            ColumnStructure,
            kpi_category
        INTO #ColumnStructures
        FROM (
            SELECT
                p1.kpi_category,
                STUFF((
                    SELECT '|' + p2.kpi_item
                    FROM dbo.ufn_get_okr_summary_filtered(@ReportYear, @ReportMonth, @businessUnit, 1, NULL) p2
                    WHERE p2.kpi_category = p1.kpi_category
                    ORDER BY p2.kpi_item_column_order
                    FOR XML PATH(''), TYPE).value('.', 'NVARCHAR(MAX)'), 1, 1, '') AS ColumnStructure
            FROM dbo.ufn_get_okr_summary_filtered(@ReportYear, @ReportMonth, @businessUnit, 1, NULL) p1
            GROUP BY p1.kpi_category
        ) AS DistinctStructures;

        DECLARE @currentStructureId INT = 1;
        DECLARE @maxStructureId INT = (SELECT MAX(StructureId) FROM #ColumnStructures);
        DECLARE @dynamicSQL NVARCHAR(MAX);
        DECLARE @params NVARCHAR(MAX);
        DECLARE @tableXml XML;

        WHILE @currentStructureId <= @maxStructureId
        BEGIN
            DECLARE @headerColumns NVARCHAR(MAX), @pivotColumns NVARCHAR(MAX), @kpiCategories NVARCHAR(MAX);

            SELECT @kpiCategories = STRING_AGG(QUOTENAME(kpi_category, ''''), ', ')
            FROM #ColumnStructures WHERE StructureId = @currentStructureId;

            SELECT @headerColumns = CAST((
                SELECT kpi_item AS [text()]
                FROM dbo.ufn_get_okr_summary_filtered(@ReportYear, @ReportMonth, @businessUnit, 1, NULL)
                WHERE kpi_category = (SELECT TOP 1 kpi_category FROM #ColumnStructures WHERE StructureId = @currentStructureId)
                ORDER BY kpi_item_column_order
                FOR XML PATH('Column'), TYPE
            ) AS NVARCHAR(MAX));

            SELECT @pivotColumns = STRING_AGG(
                '(SELECT MAX(CASE WHEN kpi_item = ' + QUOTENAME(kpi_item, '''') + ' THEN kpi_value_string END) AS [text()] FOR XML PATH(''Cell''), TYPE)',
                ','
            )
            WITHIN GROUP (ORDER BY kpi_item_column_order)
            FROM dbo.ufn_get_okr_summary_filtered(@ReportYear, @ReportMonth, @businessUnit, 1, NULL)
            WHERE kpi_category = (SELECT TOP 1 kpi_category FROM #ColumnStructures WHERE StructureId = @currentStructureId);

            SET @dynamicSQL = N'
                SELECT @tableXmlOUT = (
                    SELECT
                        (SELECT ''YTD'' AS [text()] FOR XML PATH(''Column''), TYPE),
                        CAST(@headerColumnsIN AS XML),
                        (
                            SELECT
                                (SELECT kpi_category AS [text()] FOR XML PATH(''Cell''), TYPE),
                                ' + @pivotColumns + '
                            FROM dbo.ufn_get_okr_summary_filtered(@p_CalYear, @p_CalMonth, @p_businessUnit, 1, NULL)
                            WHERE kpi_category IN (' + @kpiCategories + ')
                            GROUP BY kpi_category
                            ORDER BY kpi_category
                            FOR XML PATH(''Row''), TYPE
                        )
                    FOR XML PATH(''Table''), TYPE
                );';

            SET @params = N'
                @headerColumnsIN NVARCHAR(MAX),
                @p_CalYear INT,
                @p_CalMonth INT,
                @p_businessUnit NVARCHAR(100),
                @tableXmlOUT XML OUTPUT';
            
            EXEC sp_executesql @dynamicSQL, @params,
                @headerColumnsIN = @headerColumns,
                @p_CalYear = @ReportYear,
                @p_CalMonth = @ReportMonth,
                @p_businessUnit = @businessUnit,
                @tableXmlOUT = @tableXml OUTPUT;

            SET @allPerformanceTablesXml = CAST(CONCAT(CAST(@allPerformanceTablesXml AS NVARCHAR(MAX)), CAST(@tableXml AS NVARCHAR(MAX))) AS XML);
            
            SET @currentStructureId = @currentStructureId + 1;
        END

        IF (CAST(@allPerformanceTablesXml AS NVARCHAR(MAX))) <> ''
        BEGIN
            SELECT @performanceXml = (
                SELECT @allPerformanceTablesXml
                FOR XML PATH('Performance'), TYPE
            );
        END

        DROP TABLE #ColumnStructures;

        DECLARE @dynamicExecutionTrackerSQL NVARCHAR(MAX);
        DECLARE @executionTrackerParams NVARCHAR(MAX);
        SET @dynamicExecutionTrackerSQL = N'
            SELECT @xmlOUT = (
                SELECT
                    (
                        SELECT
                            (
                                SELECT T.v AS [text()]
                                FROM (VALUES (''Status''), (@previousMonthName), (@currentMonthName)) AS T(v)
                                FOR XML PATH(''Column''), ROOT(''Header''), TYPE
                            ),
                            (
                                SELECT
                                    (SELECT status AS [text()] FOR XML PATH(''Cell''), TYPE),
                                    (SELECT previous_value_string AS [text()] FOR XML PATH(''Cell''), TYPE),
                                    (SELECT current_value_string AS [text()] FOR XML PATH(''Cell''), TYPE)
                                FROM dbo.ufn_get_tracker_statuses_unpvt(@p_CalYear, @p_CalMonth, @p_businessUnit)
                                ORDER BY status_order
                                FOR XML PATH(''Row''), TYPE
                            )
                        FOR XML PATH(''Table''), TYPE
                    )
                FOR XML PATH(''ExecutionTracker''), TYPE
            );';

        SET @executionTrackerParams = N'
            @previousMonthName NVARCHAR(6),
            @currentMonthName NVARCHAR(6),
            @p_CalYear INT,
            @p_CalMonth INT,
            @p_businessUnit NVARCHAR(100),
            @xmlOUT XML OUTPUT';
        
        EXEC sp_executesql @dynamicExecutionTrackerSQL, @executionTrackerParams,
            @previousMonthName = @previousMonthName,
            @currentMonthName = @currentMonthName,
            @p_CalYear = @ReportYear,
            @p_CalMonth = @ReportMonth,
            @p_businessUnit = @businessUnit,
            @xmlOUT = @executionTrackerXml OUTPUT;

        -- Generate Overdue Actions Table
        SELECT @overdueActionsXml = (
            SELECT 
                (
                    SELECT
                        (SELECT T.v AS [text()] FROM (VALUES ('Action'), ('Reason')) AS T(v) FOR XML PATH('Column'), ROOT('Header'), TYPE),
                        (
                            SELECT
                                (SELECT overdue AS [text()] FOR XML PATH('Cell'), TYPE),
                                (SELECT reason AS [text()] FOR XML PATH('Cell'), TYPE)
                            FROM dbo.ufn_get_ops_overdues(@ReportYear, @ReportMonth, @businessUnit)
                            ORDER BY overdue_order
                            FOR XML PATH('Row'), TYPE
                        )
                    FOR XML PATH('Table'), TYPE
                )
            FOR XML PATH('OverdueActions'), TYPE
        );

        -- Page 1
        SELECT @page1 = (
            SELECT
                1 AS [@number],
                @businessUnit AS [Title],
                @now AS [GeneratedOn],
                @performanceXml,
                @executionTrackerXml,

                (
                    SELECT note AS [text()]
                    FROM dbo.ufn_get_commentary_details(@ReportYear, @ReportMonth, @businessUnit)
                    WHERE section = 'Highlights'
                    ORDER BY section_order, note_order
                    FOR XML PATH('KeyPoint'), ROOT('Highlights'), TYPE
                ),
                (
                    SELECT note AS [text()]
                    FROM dbo.ufn_get_commentary_details(@ReportYear, @ReportMonth, @businessUnit)
                    WHERE section = 'Challenges'
                    ORDER BY section_order, note_order
                    FOR XML PATH('KeyPoint'), ROOT('Challenges'), TYPE
                ),
                (
                    SELECT note AS [text()]
                    FROM dbo.ufn_get_commentary_details(@ReportYear, @ReportMonth, @businessUnit)
                    WHERE section = 'Opportunities'
                    ORDER BY section_order, note_order
                    FOR XML PATH('KeyPoint'), ROOT('Opportunities'), TYPE
                ),
                
                @overdueActionsXml
            FOR XML PATH('Page'), TYPE
        );

        -- Dynamically generate Priorities for Page 2
        DECLARE @prioritiesXml XML;
        DECLARE @dynamicPrioritiesSQL NVARCHAR(MAX);
        DECLARE @prioritiesParams NVARCHAR(MAX);
        DECLARE @headerPart NVARCHAR(MAX);
        DECLARE @rowPart NVARCHAR(MAX);

        IF dbo.ufn_is_priority_intro_month(@ReportMonth) = 1
        BEGIN
            SET @headerPart = N'(SELECT T.v AS [text()] FROM (VALUES (''Priority''), (''Responsible''), (''Due Date'')) AS T(v) FOR XML PATH(''Column''), ROOT(''Header''), TYPE)';
            SET @rowPart = N'(SELECT priority AS [text()] FOR XML PATH(''Cell''), TYPE), (SELECT responsible AS [text()] FOR XML PATH(''Cell''), TYPE), (SELECT due_date AS [text()] FOR XML PATH(''Cell''), TYPE)';
        END
        ELSE
        BEGIN
            SET @headerPart = N'(SELECT T.v AS [text()] FROM (VALUES (''Priority''), (''Responsible''), (''Due Date''), (''Status'')) AS T(v) FOR XML PATH(''Column''), ROOT(''Header''), TYPE)';
            SET @rowPart = N'(SELECT priority AS [text()] FOR XML PATH(''Cell''), TYPE), (SELECT responsible AS [text()] FOR XML PATH(''Cell''), TYPE), (SELECT due_date AS [text()] FOR XML PATH(''Cell''), TYPE), (SELECT status AS [text()] FOR XML PATH(''Cell''), TYPE)';
        END

        SET @dynamicPrioritiesSQL = N'
            SELECT @xmlOUT = (
                SELECT
                    (
                        SELECT
                            ' + @headerPart + ',
                            (
                                SELECT
                                    ' + @rowPart + '
                                FROM dbo.ufn_get_priorities(@p_CalYear, @p_CalMonth, @p_businessUnit)
                                ORDER BY priority_order
                                FOR XML PATH(''Row''), TYPE
                            )
                        FOR XML PATH(''Table''), TYPE
                    )
                FOR XML PATH(''Priorities''), TYPE
            );';

        SET @prioritiesParams = N'
            @p_CalYear INT,
            @p_CalMonth INT,
            @p_businessUnit NVARCHAR(100),
            @xmlOUT XML OUTPUT';
        
        EXEC sp_executesql @dynamicPrioritiesSQL, @prioritiesParams,
            @p_CalYear = @ReportYear,
            @p_CalMonth = @ReportMonth,
            @p_businessUnit = @businessUnit,
            @xmlOUT = @prioritiesXml OUTPUT;

        -- Page 2
        SELECT @page2 = (
            SELECT
                2 AS [@number],
                @prioritiesXml
            FOR XML PATH('Page'), TYPE
        );

        -- Wrap all pages in <Result>
        SELECT @unitXml = (
            SELECT @businessUnit AS [@name], @page1, @page2
            FOR XML PATH('Result'), TYPE
        );

        -- Append to final XML
        SET @xmlResult.modify('insert sql:variable("@unitXml") as last into (/Results)[1]');

        FETCH NEXT FROM unit_cursor INTO @businessUnit;
    END

    CLOSE unit_cursor;
    DEALLOCATE unit_cursor;

    SELECT '<?xml version="1.0" encoding="UTF-8"?>' + CHAR(13) + CHAR(10) + CAST(@xmlResult AS NVARCHAR(MAX)) AS XmlOutput;