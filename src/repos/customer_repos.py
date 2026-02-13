import logging

from src.domain.customer import Customer
from src.domain.loan import Loan

log = logging.getLogger(__name__)


class CustomerRepository:
    def __init__(self, client):
        self._client = client

    def add_customers(self, customers: list):
        log.info("Adding Customer Nodes to Neo4j")
        query = f""" UNWIND range(1,10) as id  
                    CREATE (c:Customer) 
                    set c.customerId= 'CUST_' + toString(id)
                    set c.name= 'Customer_' + toString(id)
                    set c.riskRating= CASE
                        WHEN id<=5 THEN 'Low'
                        WHEN id <=7 THEN 'Medium'
                        ELSE 'High'
                      END
                    RETURN c """
        self._client.run_query(query)
        log.info(f"Added {len(customers)} Customer nodes to Neo4j")

    def list_all_customers(self) -> list[Customer]:
        log.info("Listing all Customers from Neo4j")
        query = f""" MATCH (c:Customer) RETURN c """
        result = self._client.run_query(query)
        customers = list[Customer]
        for record in result:
            customer_node = record['c']
            customer = Customer(
                customer_id=customer_node['customerId'],
                name=customer_node['name'],
                risk_rating=customer_node['riskRating']
            )
            customers.append(customer)
        log.info(f"Total Customers fetched: {len(customers)}")
        return customers
