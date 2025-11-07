SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
ALTER   VIEW [dbo].[vw_okr_reporting] AS
WITH cte_last_month_with_data AS (
        SELECT
            MAX(EOMONTH(DATEFROMPARTS(od.year, v.month, 1))) AS last_month_end
        FROM
            okr_details AS od
            CROSS APPLY (
                VALUES
                    (1, od.actual_jan),
                    (2, od.actual_feb),
                    (3, od.actual_mar),
                    (4, od.actual_apr),
                    (5, od.actual_may),
                    (6, od.actual_jun),
                    (7, od.actual_jul),
                    (8, od.actual_aug),
                    (9, od.actual_sep),
                    (10, od.actual_oct),
                    (11, od.actual_nov),
                    (12, od.actual_dec)
            ) AS v(month, actual)
        WHERE
            v.actual IS NOT NULL
    ), cte_okrs AS (
SELECT
    od.item_id AS okr_id,
    omv.bu_id AS business_unit_id,
    omv.business_unit,
    omv.business_unit_alt_name,
    omv.business_segment,
    omv.value_driver,
    omv.sub_value_driver,
    omv.name AS description,
    ISNULL(omv.alt_name1, omv.name) AS kpi,
    omv.alt_name2 AS sub_kpi,
    omv.alt_name3 AS sub_kpi_2,
    omv.ppt_row_name AS ppt_row,
    omv.ppt_row_sort_order AS ppt_row_order,
    omv.ppt_column_name AS ppt_column,
    omv.ppt_column_sort_order AS ppt_column_order,
    omv.data_type,
    omv.currency AS currency_code,
    omv.aggregation_type,
    omv.metric_type_code AS metric_type,
    omv.is_dashboard_item,
    omv.is_kjops_item,
    DATEFROMPARTS(od.year, v.month, 1) AS month_date,
    od.year,
    v.month,
    v.[actual] * omv.multiplier AS actual_base,
    v.[budget] * omv.multiplier AS budget_base,
    CASE WHEN omv.data_type = 'Currency' THEN v.[actual] * omv.multiplier / ISNULL(er.rate, 1) ELSE v.[actual] * omv.multiplier END AS actual_usd,
    CASE WHEN omv.data_type = 'Currency' THEN v.[budget] * omv.multiplier / ISNULL(er.rate, 1) ELSE v.[budget] * omv.multiplier END AS budget_usd
FROM okr_details AS od
    CROSS APPLY (
        VALUES
            (1, od.actual_jan, od.budget_jan),
            (2, od.actual_feb, od.budget_feb),
            (3, od.actual_mar, od.budget_mar),
            (4, od.actual_apr, od.budget_apr),
            (5, od.actual_may, od.budget_may),
            (6, od.actual_jun, od.budget_jun),
            (7, od.actual_jul, od.budget_jul),
            (8, od.actual_aug, od.budget_aug),
            (9, od.actual_sep, od.budget_sep),
            (10, od.actual_oct, od.budget_oct),
            (11, od.actual_nov, od.budget_nov),
            (12, od.actual_dec, od.budget_dec)
    ) AS v ([month], [actual], [budget])
    CROSS JOIN cte_last_month_with_data AS lmw
    JOIN okr_master_view AS omv ON od.item_id = omv.id
    LEFT JOIN exchange_rates AS er
        ON er.to_currency_id = omv.currency_id
        AND er.from_currency_id = 2
        AND er.year = od.year
        AND er.month = v.month
WHERE omv.is_visible = 1
    AND DATEFROMPARTS(od.year, v.month, 1) <= lmw.last_month_end
), cte_aggregated AS (
SELECT
    okr_id,
    business_unit_id,
    business_unit,
    business_unit_alt_name,
    business_segment,
    value_driver,
    sub_value_driver,
    description,
    kpi,
    sub_kpi,
    sub_kpi_2,
    ppt_row,
    ppt_row_order,
    ppt_column,
    ppt_column_order,
    data_type,
    currency_code,
    aggregation_type,
    metric_type,
    is_dashboard_item,
    is_kjops_item,
    month_date,
    [year],
    [month],
    actual_base AS actual_base_mtd,
    budget_base AS budget_base_mtd,
    actual_usd AS actual_usd_mtd,
    budget_usd AS budget_usd_mtd,
    SUM(actual_base) OVER(PARTITION BY okr_id, [year] ORDER BY month_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS actual_base_ytd_sum,
    SUM(budget_base) OVER(PARTITION BY okr_id, [year] ORDER BY month_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS budget_base_ytd_sum,
    SUM(actual_usd) OVER(PARTITION BY okr_id, [year] ORDER BY month_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS actual_usd_ytd_sum,
    SUM(budget_usd) OVER(PARTITION BY okr_id, [year] ORDER BY month_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS budget_usd_ytd_sum,
    MAX(actual_base) OVER(PARTITION BY okr_id, [year], months_with_data ORDER BY month_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS actual_base_ytd_last,
    MAX(budget_base) OVER(PARTITION BY okr_id, [year], months_with_data ORDER BY month_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS budget_base_ytd_last,
    MAX(actual_usd) OVER(PARTITION BY okr_id, [year], months_with_data ORDER BY month_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS actual_usd_ytd_last,
    MAX(budget_usd) OVER(PARTITION BY okr_id, [year], months_with_data ORDER BY month_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS budget_usd_ytd_last,
    AVG(actual_base) OVER(PARTITION BY okr_id, [year] ORDER BY month_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS actual_base_ytd_avg,
    AVG(budget_base) OVER(PARTITION BY okr_id, [year] ORDER BY month_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS budget_base_ytd_avg,
    AVG(actual_usd) OVER(PARTITION BY okr_id, [year] ORDER BY month_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS actual_usd_ytd_avg,
    AVG(budget_usd) OVER(PARTITION BY okr_id, [year] ORDER BY month_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS budget_usd_ytd_avg
FROM cte_okrs
LEFT JOIN (
    SELECT
        okr_id AS okr_id2,
        month_date AS month_date2,
        COUNT(actual_usd) OVER(PARTITION BY okr_id, [year] ORDER BY month_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS months_with_data
    FROM cte_okrs
) AS md ON cte_okrs.okr_id = md.okr_id2 AND cte_okrs.month_date = md.month_date2
), cte_calculated AS (
SELECT
    okr_id,
    business_unit_id,
    business_unit,
    business_unit_alt_name,
    business_segment,
    value_driver,
    sub_value_driver,
    description,
    kpi,
    sub_kpi,
    sub_kpi_2,
    ppt_row,
    ppt_row_order,
    ppt_column,
    ppt_column_order,
    data_type,
    currency_code,
    aggregation_type,
    metric_type,
    is_dashboard_item,
    is_kjops_item,
    month_date,
    [year],
    [month],
    actual_base_mtd,
    budget_base_mtd,
    actual_usd_mtd,
    budget_usd_mtd,
    CASE
        WHEN metric_type = 'PIT' THEN actual_base_ytd_last
        WHEN aggregation_type = 'Average' THEN actual_base_ytd_avg
        ELSE actual_base_ytd_sum
    END AS actual_base_ytd,
    CASE
        WHEN metric_type = 'PIT' THEN budget_base_ytd_last
        WHEN aggregation_type = 'Average' THEN budget_base_ytd_avg
        ELSE budget_base_ytd_sum
    END AS budget_base_ytd,
    CASE
        WHEN metric_type = 'PIT' THEN actual_usd_ytd_last
        WHEN aggregation_type = 'Average' THEN actual_usd_ytd_avg
        ELSE actual_usd_ytd_sum
    END AS actual_usd_ytd,
    CASE
        WHEN metric_type = 'PIT' THEN budget_usd_ytd_last
        WHEN aggregation_type = 'Average' THEN budget_usd_ytd_avg
        ELSE budget_usd_ytd_sum
    END AS budget_usd_ytd
FROM cte_aggregated
), cte_final AS (
SELECT
    okr_id,
    business_unit_id,
    business_unit,
    business_unit_alt_name,
    business_segment,
    value_driver,
    sub_value_driver,
    description,
    kpi,
    sub_kpi,
    sub_kpi_2,
    ppt_row,
    ppt_row_order,
    ppt_column,
    ppt_column_order,
    data_type,
    currency_code,
    aggregation_type,
    metric_type,
    is_dashboard_item,
    is_kjops_item,
    month_date,
    [year],
    [month],
    actual_base_mtd,
    budget_base_mtd,
    actual_usd_mtd,
    budget_usd_mtd,
    actual_base_ytd,
    budget_base_ytd,
    actual_usd_ytd,
    budget_usd_ytd,
    LAG(actual_base_mtd) OVER(PARTITION BY okr_id ORDER BY month_date) AS pm_base_mtd,
    LAG(actual_base_ytd) OVER(PARTITION BY okr_id ORDER BY month_date) AS pm_base_ytd,
    LAG(actual_usd_mtd) OVER(PARTITION BY okr_id ORDER BY month_date) AS pm_usd_mtd,
    LAG(actual_usd_ytd) OVER(PARTITION BY okr_id ORDER BY month_date) AS pm_usd_ytd,
    LAG(actual_base_mtd) OVER(PARTITION BY okr_id, [month] ORDER BY [year]) AS py_base_mtd,
    LAG(actual_base_ytd) OVER(PARTITION BY okr_id, [month] ORDER BY [year]) AS py_base_ytd,
    LAG(actual_usd_mtd) OVER(PARTITION BY okr_id, [month] ORDER BY [year]) AS py_usd_mtd,
    LAG(actual_usd_ytd) OVER(PARTITION BY okr_id, [month] ORDER BY [year]) AS py_usd_ytd
FROM cte_calculated
)
SELECT
    f.okr_id,
    f.business_unit_id,
    f.business_segment,
    f.business_unit,
    f.business_unit_alt_name,
    f.value_driver,
    f.sub_value_driver,
    f.description,
    f.kpi,
    f.sub_kpi,
    f.sub_kpi_2,
    f.ppt_row,
    f.ppt_row_order,
    f.ppt_column,
    f.ppt_column_order,
    f.data_type,
    f.currency_code,
    f.metric_type,
    f.aggregation_type,
    f.is_dashboard_item,
    f.is_kjops_item,
    f.[year],
    f.[month],
    f.month_date,
    f.actual_base_mtd,
    f.budget_base_mtd,
    f.actual_usd_mtd,
    f.budget_usd_mtd,
    f.actual_base_ytd,
    f.budget_base_ytd,
    f.actual_usd_ytd,
    f.budget_usd_ytd,
    f.pm_base_mtd,
    f.pm_base_ytd,
    f.pm_usd_mtd,
    f.pm_usd_ytd,
    f.py_base_mtd,
    f.py_base_ytd,
    f.py_usd_mtd,
    f.py_usd_ytd,
    (ISNULL(f.actual_base_mtd,0) - ISNULL(f.budget_base_mtd,0)) / NULLIF(f.budget_base_mtd, 0) AS var_base_mtd,
    (ISNULL(f.actual_base_ytd,0) - ISNULL(f.budget_base_ytd,0)) / NULLIF(f.budget_base_ytd, 0) AS var_base_ytd,
    (ISNULL(f.actual_base_mtd,0) - ISNULL(f.pm_base_mtd,0)) / NULLIF(f.pm_base_mtd, 0) AS mom_base_mtd,
    (ISNULL(f.actual_base_ytd,0) - ISNULL(f.pm_base_ytd,0)) / NULLIF(f.pm_base_ytd, 0) AS mom_base_ytd,
    (ISNULL(f.actual_base_mtd,0) - ISNULL(f.py_base_mtd,0)) / NULLIF(f.py_base_mtd, 0) AS yoy_base_mtd,
    (ISNULL(f.actual_base_ytd,0) - ISNULL(f.py_base_ytd,0)) / NULLIF(f.py_base_ytd, 0) AS yoy_base_ytd,
    (ISNULL(f.actual_usd_mtd,0) - ISNULL(f.budget_usd_mtd,0)) / NULLIF(f.budget_usd_mtd, 0) AS var_usd_mtd,
    (ISNULL(f.actual_usd_ytd,0) - ISNULL(f.budget_usd_ytd,0)) / NULLIF(f.budget_usd_ytd, 0) AS var_usd_ytd,
    (ISNULL(f.actual_usd_mtd,0) - ISNULL(f.pm_usd_mtd,0)) / NULLIF(f.pm_usd_mtd, 0) AS mom_usd_mtd,
    (ISNULL(f.actual_usd_ytd,0) - ISNULL(f.pm_usd_ytd,0)) / NULLIF(f.pm_usd_ytd, 0) AS mom_usd_ytd,
    (ISNULL(f.actual_usd_mtd,0) - ISNULL(f.py_usd_mtd,0)) / NULLIF(f.py_usd_mtd, 0) AS yoy_usd_mtd,
    (ISNULL(f.actual_usd_ytd,0) - ISNULL(f.py_usd_ytd,0)) / NULLIF(f.py_usd_ytd, 0) AS yoy_usd_ytd
FROM cte_final AS f
GO