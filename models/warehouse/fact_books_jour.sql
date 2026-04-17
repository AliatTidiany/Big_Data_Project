SELECT
    b.intitule,
    fv.annees,
    fv.mois,
    fv.jour,
    SUM(fv.qte) AS total_qte
FROM {{ ref('fact_ventes') }} fv
JOIN {{ ref('dim_books') }} b 
    ON fv.books_id = b.id
GROUP BY 
    b.intitule,
    fv.annees,
    fv.mois,
    fv.jour