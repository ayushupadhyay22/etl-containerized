# Website Data Scraper and PostgreSQL Loader

## Project Overview

This project offers a straightforward and robust solution for extracting data from a specified website, processing it, and then storing this information persistently within a PostgreSQL database. It leverages the power of Docker and Docker Compose to establish an isolated and reproducible environment, simplifying both setup and execution. The primary goal is to automate the entire pipeline from web content retrieval to structured database population.

## Project Structure

The project is organized into a clear and intuitive directory structure to enhance readability and maintainability:


*   **`docker-compose.yml`**: This is the central configuration file for Docker Compose, acting as the blueprint for our multi-container application. It defines two primary services:
    *   **`db`**: Represents a PostgreSQL database container. It's pre-configured with essential environment variables for user credentials and database naming. A crucial health check is included to ensure the database is fully operational and ready to accept connections before any dependent services attempt to interact with it.
    *   **`app`**: Our custom Python application container. Its image is built directly from the `app/Dockerfile`. This service is responsible for executing the `data_processor.py` script. A key dependency is established, ensuring that the `app` container will only start once the `db` service has reported itself as healthy.
*   **`app/` directory**: This directory houses all the components specific to our data processing application:
    *   **`Dockerfile`**: This file provides a step-by-step guide for Docker to construct the image for our Python application. It outlines the base Python environment, specifies the installation of necessary dependencies, and copies our application's source code into the image.
    *   **`data_processor.py`**: This Python script is the operational core of our data pipeline. It encapsulates functions designed to:
        *   Fetch HTML content from a designated URL using the `requests` library.
        *   Parse the retrieved HTML to extract specific data points, leveraging the `BeautifulSoup` library.
        *   Establish a connection to the PostgreSQL database using the `psycopg2` library.
        *   Ensure the existence of the required database table (`website_data`), creating it if it's not already present.
        *   Insert the extracted and processed data into the appropriate columns of the PostgreSQL table.
    *   **`requirements.txt`**: This file explicitly lists all the third-party Python packages that `data_processor.py` relies on, such as `requests` for HTTP requests, `beautifulsoup4` for HTML parsing, and `psycopg2-binary` for PostgreSQL database interaction.

## How to Run the Project

Follow these detailed steps to successfully deploy and execute the data scraping and loading pipeline on your local development environment.

### Prerequisites

Before proceeding, please ensure that the following software is installed on your system:

*   **Docker Desktop**: This comprehensive package includes both the Docker Engine and Docker Compose, which are fundamental for running containerized applications. You can download and install it from the [official Docker website](https://www.docker.com/products/docker-desktop/).

### Step-by-Step Instructions

1.  **Clone the Repository:**
    Begin by obtaining a local copy of this project's source code. Open your preferred terminal or command prompt and execute the following command:
    ```bash
    git clone https://github.com/ayushupadhyay22/etl-containerized.git
    cd etl-containerized
    ```

2.  **Start the Pipeline with Docker Compose:**
    Navigate into the `etl-containerized` directory (if you are not already there) and then run the following command:
    ```bash
    docker compose up --build
    ```
    This single, powerful command orchestrates the entire deployment and execution process:
    *   Docker Compose will interpret the instructions laid out in the `docker-compose.yml` file.
    *   It will download the official PostgreSQL Docker image from Docker Hub (if it's not already cached locally).
    *   It will then proceed to build a custom Docker image for your Python application, following the specifications in the `app/Dockerfile`.
    *   Subsequently, it will initiate the PostgreSQL database container.
    *   Crucially, once the database container is fully operational and its health check indicates readiness to accept connections, it will then launch your Python application container.
    *   The Python application, upon starting, will establish a connection to the database, ensure the `website_data` table exists (creating it if necessary), fetch data from the pre-configured website, process this data, and finally insert it into the PostgreSQL table.

    You will observe a continuous stream of logs in your terminal, originating from both the PostgreSQL database and your data processing application. Pay close attention to messages from the `my_data_processor_app` service, which will indicate the progress of data fetching, parsing, and successful insertion into PostgreSQL.

### Verifying the Loaded Data

After the `docker compose up` command has completed its execution (or while it is still running in the background), you can easily verify that the data has been successfully loaded into your PostgreSQL instance.

1.  **Open a New Terminal Window.**
2.  **Connect to the PostgreSQL container:**
    ```bash
    docker exec -it my_postgres_db psql -U myuser -d mydatabase
    ```
    (If you have customized the `container_name`, `POSTGRES_USER`, or `POSTGRES_DB` values in your `docker-compose.yml`, please use your specific configurations here.)

3.  **Run SQL queries to inspect the data:**
    Once you are connected to the `psql` prompt, you can execute standard SQL commands to examine the database contents:
    *   **List all tables to confirm the presence of `website_data`:**
        ```sql
        \dt
        ```
    *   **Count the total number of records that have been inserted:**
        ```sql
        SELECT COUNT(*) FROM website_data;
        ```
    *   **View a sample of the loaded data to ensure correctness:**
        ```sql
        SELECT * FROM website_data LIMIT 5;
        ```
    *   **Exit the `psql` prompt:**
        ```sql
        \q
        ```

### Stopping the Project

To gracefully stop and remove all the running Docker containers, associated networks, and volumes created by Docker Compose:

```bash
docker compose down
```

This command will safely shut down both the PostgreSQL database and your application container. Importantly, your database data will be preserved within a Docker volume, meaning that if you decide to restart the project later with docker compose up, your previously loaded data will still be accessible.

## Customization
**Target Website for Scraping**: You can easily modify the website from which data is scraped by changing the WEBSITE_URL environment variable. This variable is defined within the docker-compose.yml file, specifically under the app service configuration.

**Important Note**: If you change the WEBSITE_URL to point to a different website, it is highly probable that you will need to modify the parsing logic within the app/data_processor.py script. This adjustment is necessary to correctly extract data based on the new website's unique HTML structure. The current data_processor.py is specifically tailored to scrape quotes from http://quotes.toscrape.com/.

**Database Table Structure**: Should your data requirements change, necessitating different types of information to be stored, you will need to adjust the CREATE TABLE SQL statement. This statement is located within the create_table_if_not_exists() function inside app/data_processor.py. You will need to define the appropriate column names and data types to match your new data model.
