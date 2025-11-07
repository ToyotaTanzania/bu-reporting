-- SELECT TOP 10 * FROM [dbo].[ufn_get_okr_details] (2025, 9, 1);


DECLARE @year INT = 2025;
DECLARE @month INT = 9;
DECLARE @business_unit INT = NULL; -- Set to NULL to include all business units

WITH cte_prepared AS 
(
    
SELECT
    vor.month_date,
    vor.business_unit_alt_name AS business_unit,
    vor.kpi,
    COALESCE(vor.ppt_row, vor.kpi) AS ppt_row,
    vor.ppt_row_order,
    vor.ppt_column,
    vor.ppt_column_order,
    vor.data_type,
    vor.currency_code,
    vor.aggregation_type,
    vor.actual_base_ytd,
    vor.budget_base_ytd,
    vor.var_base_ytd
FROM vw_okr_reporting AS vor
WHERE vor.is_kjops_item = 1
AND vor.[year] = @year
AND vor.[month] = @month
AND (vor.business_unit_id = @business_unit OR @business_unit IS NULL)
), cte_aggregated AS (
SELECT
    p.month_date,
    p.business_unit,
    p.ppt_row,
    p.ppt_row_order,
    p.ppt_column,
    p.ppt_column_order,
    p.data_type,
    p.currency_code,
    p.aggregation_type,
    CASE 
        WHEN p.aggregation_type = 'Average' THEN AVG(p.actual_base_ytd)
        ELSE SUM(p.actual_base_ytd)
    END AS actual,
    CASE 
        WHEN p.aggregation_type = 'Average' THEN AVG(p.budget_base_ytd)
        ELSE SUM(p.budget_base_ytd)
    END AS budget
FROM cte_prepared AS p
GROUP BY
    p.month_date,
    p.business_unit,
    p.ppt_row,
    p.ppt_row_order,
    p.ppt_column,
    p.ppt_column_order,
    p.data_type,
    p.currency_code,
    p.aggregation_type
), final_output AS (
SELECT
    a.month_date,
    a.business_unit,
    a.ppt_row,
    a.ppt_row_order,
    a.ppt_column,
    a.ppt_column_order,
    a.data_type,
    a.currency_code,
    a.actual,
    a.budget,
    CASE
        WHEN a.data_type = 'Percentage' THEN a.actual - a.budget
        ELSE (a.actual - a.budget) / NULLIF(a.budget, 0)
    END AS variance
FROM cte_aggregated AS a
)
SELECT
    f.month_date,
    f.business_unit,
    f.ppt_row_order / 100 AS table_order,
    f.ppt_row + CASE WHEN f.currency_code IS NOT NULL THEN ' (' + f.currency_code + ')' ELSE '' END AS row_header,
    f.ppt_row_order As row_order,
    COALESCE(f.ppt_column, fv.[type]) AS column_header,
    CASE 
        WHEN f.ppt_column IS NOT NULL THEN f.ppt_column_order
        WHEN fv.[type] = 'Actual' THEN 1
        WHEN fv.[type] = 'Budget' THEN 2
        WHEN fv.[type] = 'Variance' THEN 3
    END AS column_order,
    ISNULL(fv.formatted_value, '') AS formatted_value
FROM final_output AS f
CROSS APPLY (
    VALUES
        ('Actual', f.actual, FORMAT(f.actual, CASE WHEN f.data_type = 'Percentage' THEN 'P1' ELSE 'N0' END)),
        ('Budget', f.budget, FORMAT(f.budget, CASE WHEN f.data_type = 'Percentage' THEN 'P1' ELSE 'N0' END)),
        ('Variance', f.variance, FORMAT(f.variance, '+0.0%;-0.0%;0%'))
) AS fv ([type], value, formatted_value)
WHERE f.business_unit = 'Group Human Resources'
  AND (f.ppt_column IS NULL OR fv.[type] = 'Actual')
ORDER BY
    f.business_unit,
    f.ppt_row_order,
    column_order