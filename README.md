# PostgreSQL Indexing and Partitioning Performance Optimization

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-green.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Required-blue.svg)](https://www.docker.com/)
[![Typer](https://img.shields.io/badge/Typer-0.9.0+-blue.svg)](https://typer.tiangolo.com/)
[![Rich](https://img.shields.io/badge/Rich-13.7.0+-green.svg)](https://rich.readthedocs.io/)
[![Author site](https://img.shields.io/badge/author-ysskrishna.space-informational)](https://ysskrishna.space)

A PostgreSQL performance testing framework that benchmarks indexing and partitioning strategies. Helps DBAs and developers measure the real-world impact of optimization techniques through automated scenarios.

## 📊 Example Report

You can view an example report showcasing the output format and performance insights:

➡️ **[View Example Report](./media/example_reports/postgres_all_scenarios_report.html)**

## 🚀 Features

- **Comprehensive Performance Scenarios**: Comprehensive testing of various PostgreSQL optimization techniques
- **Automated Benchmarking**: Time-based performance measurements with detailed reporting
- **Docker Integration**: Easy setup with PostgreSQL 15 container
- **Rich CLI Interface**: Beautiful terminal output with progress tracking and HTML reports
- **Realistic Data Generation**: 1M+ synthetic user records for meaningful performance testing
- **Clean Architecture**: Modular design with separate setup and execution phases

## 📊 Performance Scenarios

### Indexing Strategies
- **S01**: Single Column Indexes - Basic B-tree index performance
- **S02**: Composite Indexes - Multi-column index optimization
- **S03**: Covering Indexes - Include-only queries for maximum performance
- **S04**: Unique Indexes - Constraint enforcement performance
- **S05**: Partial Indexes - Conditional indexing strategies
- **S06**: GIN Indexes - Full-text search and array operations
- **S07**: Foreign Key Indexes - Referential integrity performance
- **S08**: Bulk Loading Strategies - Data import optimization
- **S09**: Expression Indexes - Computed column indexing
- **S10**: Index Bloat - Maintenance and optimization

### Partitioning Strategies
- **S11**: Range Partitioning - Date-based table partitioning
- **S12**: List Partitioning - Categorical data partitioning
- **S13**: Materialized Views - Pre-computed result caching

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Docker and Docker Compose
- Git

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd postgres-indexing-partitioning-performance-optimization
   ```

2. **Start PostgreSQL container**
   ```bash
   docker-compose up -d
   ```

3. **Install Python dependencies**
   ```bash
   cd src
   pip install -r requirements.txt
   ```

4. **Verify setup**
   ```bash
   python cli.py list
   ```

## 🎯 Usage

### List Available Scenarios
```bash
python cli.py list
```

### Run a Specific Scenario
```bash
python cli.py run S01_single_column_index
```

### Run All Scenarios
```bash
python cli.py run-all
```

## 📁 Project Structure

```
postgres-indexing-partitioning-performance-optimization/
├── docker-compose.yml              # PostgreSQL container configuration
├── LICENSE                         # MIT License
├── README.md                       # This file
├── media/
│   └── example_reports/            # Generated HTML reports
└── src/
    ├── cli.py                      # Command-line interface
    ├── requirements.txt            # Python dependencies
    ├── scenario_manager.py         # Scenario orchestration
    ├── core/                       # Core functionality
    │   ├── base.py                 # Abstract base classes
    │   ├── benchmark.py            # Performance timing utilities
    │   ├── database.py             # Database connection management
    │   └── logger.py               # Rich console output
    ├── datasets/
    │   └── generator.py            # Synthetic data generation
    └── scenarios/                  # Performance test scenarios
        ├── base_data_setup.py      # Common data setup
        ├── S01_single_column_index/
        ├── S02_composite_indexes/
        ├── S03_covering_indexes/
        ├── S04_unique_indexes/
        ├── S05_partial_indexes/
        ├── S06_gin_indexes/
        ├── S07_foreign_key_indexes/
        ├── S08_bulk_loading_strategies/
        ├── S09_expression_indexes/
        ├── S10_index_bloat/
        ├── S11_range_partitioning/
        ├── S12_list_partitioning/
        └── S13_materialized_views/
```

## 🔧 Configuration

### Database Connection
The tool connects to PostgreSQL using these default settings:
- **Host**: localhost
- **Port**: 5432
- **Database**: master_db
- **Username**: service_user
- **Password**: service_password

### Data Generation
- **Default dataset**: 1,000,000 user records
- **Data types**: Users with demographics, timestamps, and location data

## 🧪 Testing Methodology

1. **Setup Phase**: Create tables and populate with synthetic data
2. **Execution Phase**: Measure performance without optimization,Apply optimization technique and re-measure
2. **Cleanup Phase**: Removes data, indexes, temperory tables created during setup phase


## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Built and maintained by

PostgreSQL Indexing and Partitioning Performance Optimization is built and maintained by:

| | Name | GitHub | Role |
|---|------|--------|------|
| <img src="https://github.com/ysskrishna.png?size=120" width="60" height="60" alt="Y. Siva Sai Krishna"> | **Y. Siva Sai Krishna** | [@ysskrishna](https://github.com/ysskrishna) | Creator |

## Support

If you find this project helpful:

- ⭐ Star the repository
- 🐛 [Report issues](https://github.com/ysskrishna/postgres-indexing-partitioning-performance-optimization/issues)
- 🔀 Submit pull requests
- 💝 [Sponsor on GitHub](https://github.com/sponsors/ysskrishna)

## License

MIT © [Y. Siva Sai Krishna](https://github.com/ysskrishna) — see [LICENSE](LICENSE) for details.

---

<p align="left">
  <a href="https://github.com/ysskrishna">Author's GitHub</a> •
  <a href="https://linkedin.com/in/ysskrishna">Author's LinkedIn</a> •
  <a href="https://ysskrishna.space">Author's site</a> •
  <a href="https://github.com/ysskrishna/postgres-indexing-partitioning-performance-optimization/issues">Report Issues</a>
</p>
