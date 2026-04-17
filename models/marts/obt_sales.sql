SELECT
    fv.id,
    fv.annees,
    fv.mois,
    fv.jour,
    fv.pu,
    fv.qte,

    ff.code,
    ff.qte_totale,
    ff.total_amount,
    ff.total_paid,

    c.intitule AS categorie,

    b.code AS book_code,
    b.intitule AS livre,
    b.isbn_10,
    b.isbn_13,

    cu.code AS customer_code,
    cu.nom

FROM {{ ref('fact_ventes') }} fv
JOIN {{ ref('fact_factures') }} ff ON fv.factures_id = ff.id
JOIN {{ ref('dim_books') }} b ON fv.books_id = b.id
JOIN {{ ref('dim_category') }} c ON b.category_id = c.id
JOIN {{ ref('dim_customers') }} cu ON ff.customers_id = cu.id