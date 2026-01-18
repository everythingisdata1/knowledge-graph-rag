import logging

from src.data.mock_data import stress_test_data
from src.db.neo4j_client import Neo4jClient

log = logging.getLogger(__name__)


class StressDataPreparation:
    def __init__(self, client):
        self._client = client

    def create_stress_scenarios(self):
        log.info("Creating Stress Test Scenarios in Neo4j")
        query = f""" CREATE (s:Scenario) set s+= $params RETURN s """
        for scenario in stress_test_data['SCENARIOS']:
            self._client.run_query(query, params={'params': scenario})

    def create_portfolio_nodes(self):
        log.info("Creating Portfolio Nodes in Neo4j")
        query = f""" CREATE (p:Portfolio) set p+= $params RETURN p """
        for portfolio in stress_test_data['PORTFOLIOS']:
            self._client.run_query(query, params={'params': portfolio})

    def create_customer_nodes(self):
        log.info("Creating Customer Nodes in Neo4j")
        query = f""" UNWIND range(1,5) as id  
                    CREATE (c:Customer) 
                    set c.customerId= 'CUST_' + toString(id)
                    set c.name= 'Customer_' + toString(id)
                    set c.riskRating= CASE
                        WHEN id %2 =0 THEN 'Low'
                        WHEN id <= 7 THEN 'Medium'
                        ELSE 'High'
                      END
                    RETURN c """
        self._client.run_query(query)

    def create_loan_nodes(self):
        log.info("Creating Loan Nodes in Neo4j")
        query = f""" UNWIND range(1,10) as id 
                    CREATE (l:Loan)  
                    set l.loanId= 'LOAN_' + toString(id)
                    set l.type= CASE 
                        WHEN id<= 2 THEN 'Personal Loan'
                        WHEN id <=4 THEN 'Home Loan'
                        ELSE 'Auto Loan'
                        END
                    set l.exposure= CASE 
                           WHEN id <= 2 THEN 300000 + id * 20000
                           WHEN id <= 4 THEN 1500000 + id * 100000
                           ELSE 600000 + id * 30000
                           END
                    RETURN l """
        self._client.run_query(query)
        log.info(f"Created Loan nodes in Neo4j")

    def customer_loan_relationships(self):
        log.info("Creating CUSTOMER_HAS_LOAN relationships in Neo4j")
        query = f""" match (c:Customer) , (l:Loan)
          where toInteger(substring(c.customerId,5))=toInteger(substring(l.loanId,5)) % 10 +1
          CREATE (c)-[r:CUSTOMER_HAS_LOAN]->(l) RETURN c, l """
        self._client.run_query(query)

    def loan_portfolio_relationships(self):
        log.info("Creating LOAN_IN_PORTFOLIO relationships in Neo4j")
        query = """ match (l:Loan) with l, 
                    CASE 
                    WHEN l.type=  'Personal Loan' THEN 'Retail'
                    WHEN l.type= 'Home Loan' THEN 'Housing'
                    ELSE 'Auto' 
                    END 
                    as portfolio_name 
                    match (p:Portfolio {name:l.portfolio_name} )
                    CREATE (l)-[r:LOAN_BELONGS]->(p) RETURN l, p """
        self._client.run_query(query)

    def loan_pd_relationships(self):
        log.info("Creating LOAN_HAS_PD relationships in Neo4j")
        query = """ match (l:Loan) 
                    CREATE (pd:PD {
                        value: CASE  
                            WHEN l.type= 'Personal Loan' THEN round(0.35 + rand() * 0.25, 2)
                            WHEN l.type= 'Home Loan' THEN round(0.30 + rand() * 0.20, 2) 
                            ELSE round(0.10 + rand() * 0.15, 2)  
                        END,
                        modelVersion: 'PD_v3.2'
                    }) 
                    CREATE (l)-[r:LOAN_HAS_PD]->(pd) RETURN l, pd """
        self._client.run_query(query)

    def loan_lgd_relationships(self):
        log.info("Creating LOAN_HAS_LGD relationships in Neo4j")
        query = """ match (l:Loan) 
        CREATE (lgd:LGD {
        value: CASE 
            WHEN l.type='Personal Loan' THEN round(0.50 + rand() * 0.20, 2)
            WHEN l.type='Home Loan' THEN round(0.30 + rand() * 0.20, 2)
            ELSE round(0.20 + rand() * 0.15, 2)
        END,
        modelVersion: 'LGD_v2.1'
        })
        create (l)-[r:LOAN_HAS_LGD]->(lgd) RETURN l, lgd """
        self._client.run_query(query)

    def loan_ecl_relationship(self):
        log.info("Creating LOAN_HAS_ECL relationships in Neo4j Exposure * PD * LGD")
        query = """ match (l:Loan)-[r1:LOAN_HAS_PD]->(pd:PD),(l)-[r2:LOAN_HAS_LGD]->(lgd:LGD)  
                    with l,    pd, lgd, round(l.exposure * pd.value * lgd.value,2) as ecl_value
                    CREATE (ecl:ECL )
                    set ecl.value= ecl_value
                    set ecl.stage= CASE 
                        WHEN pd.value < 0.2 THEN 'Stage 1'
                        WHEN pd.value < 0.5 THEN 'Stage 2'
                        ELSE 'Stage 3'
                        END
                    set ecl.calculationDate= date('2024-12-31')                 
                    with l, ecl
                    match (s:Scenario {name: '2024_Severe_Stress'}), (m:RiskModel {name: 'IFRS9_ECL_Model'})
                    CREATE 
                    (l)-[r1:LOAN_HAS_ECL {scenario:s.name, modelVersion:m.version}]->(ecl),
                    (ecl)-[r2:CALCULATED_UNDER]->(s),
                    (s)-[r3:USES_MODEL]->(r)
                    RETURN l, ecl, s, r """
        self._client.run_query(query)


if __name__ == '__main__':
    with Neo4jClient(load_schema=True) as client:
        data_prep = StressDataPreparation(client)

        data_prep.create_stress_scenarios()
        data_prep.create_portfolio_nodes()
        data_prep.create_customer_nodes()
        data_prep.create_loan_nodes()
        data_prep.customer_loan_relationships()
        data_prep.loan_portfolio_relationships()
        data_prep.loan_pd_relationships()
        data_prep.loan_lgd_relationships()
        data_prep.loan_ecl_relationship()
