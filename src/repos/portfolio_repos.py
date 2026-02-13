import logging

log = logging.getLogger(__name__)


class PortfolioRepository:
    def __init__(self, client):
        self._client = client

    def add_portfolios(self, portfolios: list):
        log.info("Adding Portfolio Nodes to Neo4j")
        query = """ UNWIND $portfolios as portfolio 
                 CREATE (p:Portfolio) 
                 set p.name= portfolio.name
                 set p.segment= portfolio.segment
                 RETURN p """
        self._client.run_query(query, params={'portfolios': portfolios})

    def list_all_portfolios(self) -> list:
        log.info(f"Listing all Portfolios from Neo4j")
        query = """ Match (p:Portfolio) RETURN p """
        result = self._client.run_query(query)
        portfolios = []
        for record in result:
            portfolio_node = record['p']
            portfolio = {
                'name': portfolio_node['name'],
                'segment': portfolio_node['segment']
            }
            portfolios.append(portfolio)
        log.info(f"Total Portfolios fetched: {len(portfolios)}")
        return portfolios
