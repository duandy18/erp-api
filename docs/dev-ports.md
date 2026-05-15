# ERP 本地端口合同

ERP 不直接读取 WMS / PMS / OMS / Procurement / Logistics 数据库。

## ERP

| System | API | Web | DB |
|---|---:|---:|---|
| ERP | 7990 | 5170 | 5433/erp |

## Existing Apps

| System | API | Web | DB |
|---|---:|---:|---|
| WMS | 8000 | 5173 | 5433/wms |
| PMS | 8005 | 5174 | 5433/pms |
| OMS | 8010 | 5175 | 5433/oms |
| Procurement | 8015 | 5176 | 5433/procurement |
| Logistics | 8020 | 5177 | 5433/logistics |

## Future Gateway

| Component | Local Port |
|---|---:|
| ERP Gateway | 7080 |
