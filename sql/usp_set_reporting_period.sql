SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
ALTER PROCEDURE [dbo].[usp_set_reporting_period]
    @CalYear INT,
    @CalMonth INT,
    @UserID INT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;
    
    IF NOT EXISTS (SELECT 1 FROM dbo.users WHERE is_admin = 1)
    BEGIN
        THROW 50002, 'Access Denied: This operation requires administrator privileges.', 1;
    END

    IF @CalYear IS NULL OR @CalYear < 2025
    BEGIN
        THROW 50000, 'Year cannot be less than 2025.', 1;
    END

    IF NOT (@CalMonth BETWEEN 1 AND 12)
    BEGIN
        THROW 50001, 'Month must be between 1 and 12.', 1;
    END

    BEGIN TRY
        MERGE INTO dbo.submission_period AS Target
        USING (SELECT 1 AS a) AS Source
        ON 1 = 1

        WHEN MATCHED AND (Target.[year] <> @CalYear OR Target.[month] <> @CalMonth) THEN
            UPDATE SET
                Target.[year] = @CalYear,
                Target.[month] = @CalMonth,
                Target.period_closed_at = NULL,
                Target.updated_at = GETUTCDATE(),
                Target.updated_by_id = @UserID

        WHEN NOT MATCHED BY TARGET THEN
            INSERT ([year], [month], period_closed_at, updated_by_id)
            VALUES (@CalYear, @CalMonth, NULL, @UserID);

        IF @@ROWCOUNT = 0
        BEGIN
            THROW 50002, 'No changes were made to the reporting period.', 1;
        END

    END TRY
    BEGIN CATCH
        THROW;
    END CATCH
END
GO
