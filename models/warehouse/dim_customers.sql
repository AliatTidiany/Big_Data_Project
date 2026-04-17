SELECT
    id,
    code,
    first_name,
    last_name,
    first_name || ' ' || last_name AS nom,
    created_at
FROM {{ ref('stg_CUSTOMERS') }}