let
    Source = Parquet.Document(File.Contents(RetailParquetPath)),
    Types = Table.TransformColumnTypes(Source, {
        {"invoice_no", type text}, {"stock_code", type text},
        {"invoice_date", type datetime}, {"customer_id", Int64.Type},
        {"quantity", type number}, {"unit_price", type number},
        {"line_value", type number}, {"country", type text}
    }),
    AddOrderDate = Table.AddColumn(Types, "OrderDate", each Date.From([invoice_date]), type date)
in
    AddOrderDate
