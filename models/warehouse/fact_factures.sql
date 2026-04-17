SELECT
    *,
    YEAR(date_edit) AS annees,
    MONTHNAME(date_edit) AS mois,
    DAYNAME(date_edit) AS jour
FROM {{ ref('stg_FACTURES') }}