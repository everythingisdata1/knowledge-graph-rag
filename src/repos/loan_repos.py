import logging

from src.domain.loan import Loan

log = logging.getLogger(__name__)


class LoanRepository:
    def __init__(self, client):
        self._client = client

    def add_loans(self, loans: list[Loan]):
        log.info("Adding Loan Nodes to Neo4j")
        query = f""" UNWIND range(1,20) as id 
                        create (l:Loan)  
                        set l.loanId= 'LOAN_' + toString(id)
                        set l.type= CASE 
                            WHEN id<= 7 THEN 'Personal Loan'
                            WHEN id <=14 THEN 'Home Loan'
                            ELSE 'Auto Loan'
                            END
                        set l.exposure= CASE 
                               WHEN id <= 7 THEN 300000 + id * 20000
                               WHEN id <= 14 THEN 1500000 + id * 100000
                               ELSE 600000 + id * 30000
                               END
                        RETURN l """

        self._client.run_query(query)
        log.info(f"Added {len(loans)} Loan nodes to Neo4j")

    def list_all_loans(self) -> list[Loan]:
        log.info("Listing all Loans from Neo4j")
        query = f""" MATCH (l:Loan) RETURN l """
        result = self._client.run_query(query)
        loans = []
        for record in result:
            loan_node = record['l']
            loan = Loan(
                loan_id=loan_node['loanId'],
                type=loan_node['type'],
                exposure=loan_node['exposure']
            )
            loans.append(loan)
        log.info(f"Total Loans fetched: {len(loans)}")
        return loans
