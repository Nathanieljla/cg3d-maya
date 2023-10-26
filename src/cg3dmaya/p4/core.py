from P4 import P4
#https: // stackoverflow.com / questions / 46726545 / authenticating - and-authorizing - users - securely - in-a - python - pyqt - desktop - applicati

p4agent = P4()
p4agent.port = "ssl:azhcprd01.madisoncollege.edu:1666"
p4agent.user = "nalbright_admin"
p4agent.password = ""
p4agent.connect()
p4agent.run_login()