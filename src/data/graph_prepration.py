import logging

from src.data.sample_data import stress_test_data
from src.db.neo4j_client import Neo4jClient
from src.repos.customer_repos import CustomerRepository
from src.repos.loan_repos import LoanRepository

log = logging.getLogger(__name__)


class StressDataPreparation:
    def __init__(self, client):
        self._client = client

    def create_stress_scenarios(self):
        log.info("Creating Stress Test Scenarios in Neo4j")
        query = f""" CREATE (s:Scenario) set s+= $params RETURN s """
        for scenario in stress_test_data['SCENARIOS']:
            self._client.run_query(query, params={'params': scenario})

        log.info("Creating Portfolio Nodes in Neo4j")
        query = f""" CREATE (p:Portfolio) set p+= $params RETURN p """
        for portfolio in stress_test_data['PORTFOLIOS']:
            self._client.run_query(query, params={'params': portfolio})

        log.info(f"Creating Customer Nodes in Neo4j")
        CustomerRepository(self._client).add_customers([])

        log.info(f"Creating Loan Nodes in Neo4j")
        LoanRepository(self._client).add_loans([])

        log.info("Creating CUSTOMER_HAS_LOAN relationships in Neo4j")
        query = f""" match (c:Customer) , (l:Loan)
          where toInteger(substring(c.customerId,5))=toInteger(substring(l.loanId,5)) % 10 +1
          CREATE (c)-[r:CUSTOMER_HAS_LOAN]->(l) RETURN c, l """
        self._client.run_query(query)

        log.info("Creating LOAN_IN_PORTFOLIO relationships in Neo4j")
        query = """ match (l:Loan) with l, 
                    CASE 
                    WHEN l.type=  'Personal Loan' THEN 'Retail'
                    WHEN l.type= 'Home Loan' THEN 'Housing'
                    ELSE 'Auto' 
                    END 
                    as portfolio_name 
                    match (p:Portfolio {name:portfolio_name} )
                    CREATE (l)-[r:LOAN_BELONGS]->(p) RETURN l, p """
        self._client.run_query(query)

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
                    (l)-[r1:LOAN_HAS_ECL {scenario:s.name, modelVersion:m.version}]->(ecl)-[r2:UNDER_SCENARIO]->(s),
                    (s)-[r3:USES_MODEL]->(m)
                    RETURN l, ecl, s, m """
        self._client.run_query(query)


if __name__ == '__main__':
    with Neo4jClient(load_schema=True) as client:
        data_prep = StressDataPreparation(client)

        data_prep.create_stress_scenarios()
