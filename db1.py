import mysql.connector
from mysql.connector.cursor import MySQLCursor

# TODO: Make parameter order uniform, current discrepencies are confusing in some cases, eg property
# Ensure cursors are closed after using in each function
# Replicate search functions with more combinations of paramaters
# Make the dictionary predicter adaptive
# Fix fetchfielddb2

investorFields = {
    'investorID': 0,
    'fname' : 1,
    'lname' : 2,
    'password' : 3
}

agentFields = {
    'agentID' : 0,
    'fname' : 1,
    'lname' : 2,
    'pSold' : 3
}

propertyFields = {
    'mlsID' : 0,
    'price' : 1,
    'sqft' : 2,
    'status' : 3,
    'address' : 4,
    'city' : 5,
    'subzone' : 6,
    'rent' : 7
}

criteriaFields = {
    'investorID' : 0,
    'costs' : 1,
    'coc' : 2,
    'dsr' : 3,
    'price_limit': 4,
    'ir' : 5,
    'cap' : 6,
    'mgLength' : 7,
    'price_min' : 8
}

representsFields = {
    'agentID' : 0,
    'investorID' : 1
}

def establishConnection():
    cnx = mysql.connector.connect(user='root', password='$quareUpCowboy',
                                    host='127.0.0.1',
                                    database='reProj',
                                    auth_plugin = 'mysql_native_password',
                                    buffered = True
                                    )
    return(cnx)

class State:
    def __init__(self, name):
        self.name = name

class City:
    def __init__(self, name, state):
        self.name = name
        self.state = state

class Subzone:
    def __init__(self, name, state, city):
        self.name = name
        self.state = state
        self.city = city

class House:
    def __init__(self, price, sqft, sZone, status, mlsID, address, rent, tax, city):
        self.price = price
        self.sqft = sqft
        self.sZone = sZone
        self.status = status
        self.mlsID = mlsID
        self.address = address
        self.rent = rent
        self.tax = tax
        self.city = city

def dumpToHouse(dump):
    if(len(dump)==0):
        print("No Property Found.")
        return([])
    else:
        house = House(dump[1],dump[2],dump[6],dump[3],dump[0],dump[4],dump[7],dump[8],dump[5])
        return(house)

class Agent:
    def __init__(self, pSold, fName, lName, agentID, password):
        self.pSold = pSold
        self.fName = fName
        self.lName = lName 
        self.agentID = agentID
        self.password = password

def dumpToAgent(dump):
    if(len(dump)==0):
        print("No Agent Found.")
        return([])
    else:
        agent = Agent(dump[3],dump[1],dump[2],dump[0],dump[4])
        return(agent)

class Investor:
    def __init__(self, fName, lName, investorID, password):
        self.fName = fName
        self.lName = lName
        self.investorID = investorID
        self.password = password

def dumpToInvestor(dump):
    if(len(dump)==0):
        print("No Investor Found.")
        return([])
    else:
        investor = Investor(dump[1],dump[2],dump[0],dump[3])
        return(investor)

class Criteria:
    def __init__(self, investorID, mgLen, costs, coc, ir, cap, dsr, lim, min, down):
        self.investorID = investorID
        self.mgLen = mgLen
        self.costs = costs
        self.coc = coc
        self.ir = ir
        self.cap = cap
        self.dsr = dsr
        self.lim = lim
        self.min = min
        self.down = down

def dumpToCriteria(dump):
    if(len(dump)==0):
        print("No Criteria Found.")
        return([])
    else:
        crit = Criteria(dump[0],dump[7],dump[1],dump[2],dump[5],dump[6],dump[3],dump[4],dump[8],dump[9])
        return(crit)

def calMortgage(price, ir, mgLen, down):
    price = (1-(down/100))*price
    terms = mgLen * 12
    ir = ir/(100*12)
    numerator = ((1+ir)**terms)
    denominator = (((1+ir)**terms) - 1)
    return (price*ir*numerator/denominator)

def calNOI (house, criteria):
    moCost = criteria.costs + (house.tax / 12)
    noi = ((house.rent - moCost) * 12)
    return noi

def calCap (house, criteria):
    noi = calNOI (house, criteria)
    return (noi/house.price*100)

def calDSR (house, criteria):
    noi = calNOI(house, criteria)
    mort = calMortgage(house.price, criteria.ir, criteria.mgLen, criteria.down)*12
    return (noi/mort)

def calSubzoneRent(city, subzone):
    cnx = establishConnection()
    curA = MySQLCursor(cnx)
    query = "SELECT * FROM property WHERE city = %s AND subzone = %s"
    params = [city, subzone]
    curA.execute(query, params)
    dump = curA.fetchall()
    curA.close()
    rent = 0

    if(len(dump) == 0):
        print("No houses in city/szone")
        return(0)
    else:
        for house in dump:
            rent += fetchFieldDB2([house], 'rent')
        return(rent/(len(dump)))
    
def calSubzonePrice(city, subzone):
    cnx = establishConnection()
    curA = MySQLCursor(cnx)
    query = "SELECT * FROM property WHERE city = %s AND subzone = %s"
    params = [city, subzone]
    curA.execute(query, params)
    dump = curA.fetchall()
    curA.close()
    price = 0

    if(len(dump) == 0):
        print("No houses in city/szone")
        return(0)
    else:
        for house in dump:
            price += fetchFieldDB2([house], 'price')
        return(price/(len(dump)))

def addAgentDB (agent):
    # Check if existing by investorID
    # Format data
    # Run and commit query
    cnx = establishConnection()
    curA = MySQLCursor(cnx)
    query = "SELECT * FROM agent WHERE agentID = %s"
    params = [agent.agentID,]
    curA.execute(query, params)
    curA.fetchall()

    if (curA.rowcount>0):
        print("Agent Already Exists")
        curA.fetchall() #fetchall clears cursor, sql hates full buffers
        curA.close()
        cnx.close()
    elif (curA.rowcount <= 0):
            curA = MySQLCursor(cnx)
            query = "INSERT INTO agent (agentID, fname, lname, pSold, password) VALUES(%s,%s,%s,%s,%s)"
            params = [agent.agentID,agent.fName,agent.lName,agent.pSold,agent.password]
            curA.execute(query,params)
            cnx.commit()
            curA.fetchall()
            curA.close()
            cnx.close()

def addInvestorDB (investor):
    cnx = establishConnection()
    curA = MySQLCursor(cnx)
    query = "SELECT * FROM investor WHERE investorID = %s"
    params = [investor.investorID,]
    curA.execute(query, params)
    curA.fetchall()

    if (curA.rowcount>0):
        print("Investor Already Exists")
        curA.fetchall() #fetchall clears cursor, sql hates full buffers
        curA.close()
        cnx.close()
    elif (curA.rowcount <= 0):
        curA.close()
        curA = MySQLCursor(cnx)
        query = "INSERT INTO investor (investorID, fname, lname) VALUES(%s,%s,%s)"
        params = [investor.investorID,investor.fName,investor.lName]
        curA.execute(query,params)
        cnx.commit()
        curA.fetchall()
        curA.close()
        cnx.close()

def addHouseDB (house):
    cnx = establishConnection()
    curA = MySQLCursor(cnx)
    query = "SELECT * FROM property WHERE mlsID = %s"
    params = [house.mlsID,]
    curA.execute(query, params)
    curA.fetchall()
    curA.close()

    if (curA.rowcount>0):
        print("House Already Exists")
        curA.fetchall()
        curA.close()
        cnx.close()
    elif (curA.rowcount <= 0): 
        curA = MySQLCursor(cnx)
        query = "INSERT INTO property (mlsID, price, sqft, status, address, city, subzone, rent) VALUES(%s,%s,%s,%s,%s,%s,%s)"
        params = [house.mlsID, house.price, house.sqft, house.status, house.address, house.city, house.sZone, house.rent]
        curA.execute(query,params)
        cnx.commit()
        curA.fetchall()
        curA.close()
        cnx.close()

def addCriteriaDB (criteria):
    cnx = establishConnection()
    curA = MySQLCursor(cnx)
    query = "SELECT * FROM criteria WHERE investorID = %s"
    params = [criteria.investorID,]
    curA.execute(query, params)
    curA.fetchall()

    if (curA.rowcount>0):
        print("Criteria Already Exists")
        curA.fetchall()
        curA.close()
        cnx.close()
    elif (curA.rowcount <= 0): 
        curA = MySQLCursor(cnx)
        query = "INSERT INTO criteria (investorID, costs, coc, dsr, price_limit, ir, cap, mgLength, price_min) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        params = [criteria.investorID, criteria.costs, criteria.coc, criteria.dsr, criteria.lim, criteria.ir, criteria.cap, criteria.mgLen, criteria.min]
        curA.execute(query,params)
        cnx.commit()
        curA.fetchall()
        curA.close()
        cnx.close()
    
def addRepDB (agent,investor):
    cnx = establishConnection()
    curA = MySQLCursor(cnx)
    query = "SELECT * FROM represents WHERE agentID = %s AND investorID = %s"
    params = [investor.investorID,agent.agentID]
    curA.execute(query, params)
    curA.fetchall()

    if (curA.rowcount>0):
        print("Relation Already Exists")
        curA.fetchall()
        curA.close()
        cnx.close()
    elif (curA.rowcount <= 0):
        curA = MySQLCursor(cnx)
        query = "INSERT INTO represents (agentID, investorID) VALUES(%s,%s)"
        params = [agent.agentID,investor.investorID]
        curA.execute(query,params)
        cnx.commit()
        curA.fetchall()
        curA.close()
        cnx.close()

def updateHouseDB(house):
    cnx = establishConnection()
    curA = MySQLCursor(cnx)
    query = "SELECT * FROM property WHERE mlsID = %s"
    params = [house.mlsID,]
    curA.execute(query, params)
    curA.fetchall()

    if (curA.rowcount <= 0):
        print("Property Not Found")
        curA.fetchall()
        curA.close()
        cnx.close()
    elif (curA.rowcount > 0):
        curA = MySQLCursor(cnx)
        query = "UPDATE property SET price = %s, rent = %s, sqft = %s, status = %s, address = %s, city = %s, subzone = %s WHERE mlsID = %s"
        params = [house.price, house.rent, house.sqft, house.status, house.address, house.city, house.sZone, house.mlsID]
        curA.execute(query,params)
        cnx.commit()
        curA.fetchall()
        curA.close()
        cnx.close()

def updateAgentDB(agent):
    cnx = establishConnection()
    curA = MySQLCursor(cnx)
    query = "SELECT * FROM agent WHERE agentID = %s"
    params = [agent.agentID,]
    curA.execute(query, params)
    curA.fetchall()

    if (curA.rowcount <= 0):
        print("Agent Not Found")
        curA.fetchall() 
        curA.close()
        cnx.close()
    elif (curA.rowcount > 0):
        curA = MySQLCursor(cnx)
        query = "UPDATE agent SET fname = %s, lname = %s, pSold = %s, password WHERE agentID = %s"
        params = [agent.fName, agent.lName, agent.pSold, agent.agentID, agent.password]
        curA.execute(query,params)
        cnx.commit()
        curA.fetchall()
        curA.close()
        cnx.close()
        
def updateCriteriaDB(criteria):
    cnx = establishConnection()
    curA = MySQLCursor(cnx)
    query = "SELECT * FROM criteria WHERE investorID = %s"
    params = [criteria.investorID,]
    curA.execute(query, params)
    curA.fetchall()

    if (curA.rowcount <= 0):
        print("Criteria Not Found")
        curA.fetchall() 
        curA.close()
        cnx.close()
    elif (curA.rowcount > 0):
        curA = MySQLCursor(cnx)
        query = "UPDATE criteria SET costs= %s, coc= %s, dsr= %s, price_limit= %s, price_min = %s, ir= %s, cap= %s, mgLength= %s, percentDown = %s WHERE investorID = %s"
        params = [criteria.costs, criteria.coc, criteria.dsr, criteria.lim, criteria.min, criteria.ir, criteria.cap, criteria.mgLen,criteria.down,criteria.investorID]
        curA.execute(query,params)
        cnx.commit()
        curA.fetchall()
        curA.close()
        cnx.close()

def updateInvestorDB(investor):
    cnx = establishConnection()
    curA = MySQLCursor(cnx)
    query = "SELECT * FROM investor WHERE investorID = %s"
    params = [investor.investorID,]
    curA.execute(query, params)
    curA.fetchall()

    if (curA.rowcount <= 0):
        print("Investor Not Found")
        curA.fetchall() 
        curA.close()
    elif (curA.rowcount > 0):
        curA = MySQLCursor(cnx)
        query = "UPDATE investor SET fname = %s, lname = %s, password = %s WHERE investorID = %s"
        params = [investor.fName, investor.lName, investor.investorID, investor.password]
        curA.execute(query,params)
        cnx.commit()
        curA.fetchall()
        curA.close()

# Unneccesary?
# def updateRepDB(investor, agent):
def delAgentDB(agent):
    cnx = establishConnection()
    curA = MySQLCursor(cnx)
    query = "SELECT * FROM agent WHERE agentID = %s"
    params = [agent.agentID,]
    curA.execute(query, params)
    curA.fetchall()

    if (curA.rowcount<=0):
        print("Agent Not Found")
        curA.fetchall()
        curA.close()
        cnx.close()
    elif (curA.rowcount > 0):
        curA = MySQLCursor(cnx)
        query = "DELETE FROM agent WHERE agentID = %s" 
        params = [agent.agentID]
        curA.execute(query,params)
        cnx.commit()
        curA.fetchall()
        curA.close()
        cnx.close()

def delHouseDB(house):
    cnx = establishConnection()
    curA = MySQLCursor(cnx)
    query = "SELECT * FROM property WHERE mlsID = %s"
    params = [house.mlsID,]
    curA.execute(query, params)
    curA.fetchall()

    if (curA.rowcount <= 0):
        print("Property Not Found")
        curA.fetchall() 
        curA.close()
        cnx.close()
    elif (curA.rowcount > 0):
        curA = MySQLCursor(cnx)
        query = "DELETE FROM property WHERE mlsID = %s"
        params = [house.mlsID,]
        curA.execute(query,params)
        cnx.commit()
        curA.fetchall()
        curA.close()
        cnx.close()
        
def delCriteriaDB(criteria):
    cnx = establishConnection()
    curA = MySQLCursor(cnx)
    query = "SELECT * FROM criteria WHERE investorID = %s"
    params = [criteria.investorID,]
    curA.execute(query, params)
    curA.fetchall()

    if (curA.rowcount <= 0):
        print("Criteria Not Found")
        curA.fetchall() 
        curA.close()
        cnx.close()
    elif (curA.rowcount > 0):
        curA = MySQLCursor(cnx)
        query = "DELETE FROM criteria WHERE investorID = %s"
        params = [criteria.investorID,]
        curA.execute(query,params)
        cnx.commit()
        curA.fetchall()
        curA.close()
        cnx.close()

def delInvestorDB(investor):
    cnx = establishConnection()
    curA = MySQLCursor(cnx)
    query = "SELECT * FROM investor WHERE investorID = %s"
    params = [investor.investorID,]
    curA.execute(query, params)
    curA.fetchall()

    if (curA.rowcount <= 0):
        print("Investor Not Found")
        curA.fetchall() 
        curA.close()
        cnx.close()
    elif (curA.rowcount > 0):
        curA = MySQLCursor(cnx)
        query = "DELETE FROM investor WHERE investorID = %s"
        params = [investor.investorID,]
        curA.execute(query,params)
        cnx.commit()
        curA.fetchall()
        curA.close()
        cnx.close()

def delRepDB(investor, agent):
    cnx = establishConnection()
    curA = MySQLCursor(cnx)
    query = "SELECT * FROM represents WHERE investorID = %s AND agentID = %s"
    params = [investor.investorID,agent.agentID]
    curA.execute(query, params)
    curA.fetchall()

    if (curA.rowcount <= 0):
        print("Relation Not Found")
        curA.fetchall()
        curA.close()
        cnx.close()
    elif (curA.rowcount > 0):
        curA = MySQLCursor(cnx)
        query = "DELETE FROM represents WHERE agentID = %s AND investorID = %s"
        params = [agent.agentID, investor.investorID]
        curA.execute(query,params)
        cnx.commit()
        curA.fetchall()
        print("Record Deleted")
        curA.close()
        cnx.close()

def fetchAgentDB(agentID, pWord):
    cnx = establishConnection()
    curA = MySQLCursor(cnx)
    query = "SELECT * FROM agent WHERE agentID = %s AND password = %s"
    params = [agentID, pWord]
    curA.execute(query, params)
    curA.fetchall()

    if (curA.rowcount <= 0):
        print("Incorrect info. Unable to retrieve agent.")
        curA.fetchall()
        curA.close()
        cnx.close()
        return([])
    elif (curA.rowcount > 0):
        curA = MySQLCursor(cnx)
        query = "SELECT * FROM agent WHERE agentID = %s"
        params = [agentID,]
        curA.execute(query,params)
        dump = curA.fetchall()
        curA.close()
        cnx.close()
        return(dump)

def fetchHouseDB(mlsID):
    cnx = establishConnection()
    curA = MySQLCursor(cnx)
    query = "SELECT * FROM property WHERE mlsID = %s"
    params = [mlsID,]
    curA.execute(query, params)
    curA.fetchall()

    if (curA.rowcount <= 0):
        print("Property Not Found")
        curA.fetchall() 
        curA.close()
        cnx.close()
        return([])
    elif (curA.rowcount > 0):
        curA = MySQLCursor(cnx)
        query = "SELECT * FROM property WHERE mlsID = %s"
        params = [mlsID,]
        curA.execute(query,params)
        dump = curA.fetchall()
        curA.close()
        cnx.close()
        return(dump)

def fetchHouseByCityDB(city):
    cnx = establishConnection()
    curA = MySQLCursor(cnx)
    query = "SELECT * FROM property WHERE city = %s"
    params = [city,]
    curA.execute(query, params)
    curA.fetchall()

    if (curA.rowcount <= 0):
        print("Property Not Found")
        curA.fetchall() 
        curA.close()
        cnx.close()
        return([])
    elif (curA.rowcount > 0):
        curA.close()
        curA = MySQLCursor(cnx)
        query = "SELECT * FROM property WHERE city = %s"
        params = [city,]
        curA.execute(query,params)
        dump = curA.fetchall()
        curA.close()
        cnx.close()
        return(dump)

def fetchCriteriaDB(investorID):
    cnx = establishConnection()
    curA = MySQLCursor(cnx)
    query = "SELECT * FROM criteria WHERE investorID = %s"
    params = [investorID,]
    curA.execute(query, params)
    curA.fetchall()

    if (curA.rowcount <= 0):
        print("Criteria Not Found")
        curA.fetchall()
        curA.close()
        cnx.close()
        return([])
    elif (curA.rowcount > 0):
        curA = MySQLCursor(cnx)
        query = "SELECT * FROM criteria WHERE investorID = %s"
        params = [investorID,]
        curA.execute(query,params)
        dump = curA.fetchall()
        curA.close()
        cnx.close()
        return(dump)

def fetchInvestorDB(investorID, pWord):
    cnx = establishConnection()
    curA = MySQLCursor(cnx)
    query = "SELECT * FROM investor WHERE investorID = %s AND password = %s"
    params = [investorID,pWord]
    curA.execute(query, params)
    curA.fetchall()

    if (curA.rowcount <= 0):
        print("Investor Not Found")
        curA.fetchall() 
        curA.close()
        cnx.close()
        return([])
    elif (curA.rowcount > 0):
        curA = MySQLCursor(cnx)
        query = "SELECT * FROM investor WHERE investorID = %s"
        params = [investorID,]
        curA.execute(query,params)
        dump = curA.fetchall()
        curA.close()
        cnx.close()
        return(dump)

def fetchInvestorDB2(investorID):
    cnx = establishConnection()
    curA = MySQLCursor(cnx)
    query = "SELECT * FROM investor WHERE investorID = %s"
    params = [investorID,]
    curA.execute(query, params)
    curA.fetchall()

    if (curA.rowcount <= 0):
        print("Investor Not Found")
        curA.fetchall() 
        curA.close()
        cnx.close()
        return([])
    elif (curA.rowcount > 0):
        curA = MySQLCursor(cnx)
        query = "SELECT * FROM investor WHERE investorID = %s"
        params = [investorID,]
        curA.execute(query,params)
        dump = curA.fetchall()
        curA.close()
        cnx.close()
        return(dump)

def fetchRepDB(investorID, agentID):
    cnx = establishConnection()
    curA = MySQLCursor(cnx)
    query = "SELECT * FROM represents WHERE investorID = %s AND agentID = %s"
    params = [investorID,agentID]
    curA.execute(query, params)
    curA.fetchall()

    if (curA.rowcount <= 0):
        print("Relation Not Found")
        curA.fetchall()
        curA.close()
        cnx.close()
        return([])
    elif (curA.rowcount > 0):
        curA = MySQLCursor(cnx)
        query = "SELECT * FROM represents WHERE agentID = %s AND investorID = %s"
        params = [agentID,investorID]
        curA.execute(query,params)
        dump = curA.fetchall()
        curA.close()
        cnx.close()
        return(dump)

def fetchRepByAgentDB(agentID):
    cnx = establishConnection()
    curA = MySQLCursor(cnx)
    query = "SELECT * FROM represents WHERE agentID = %s"
    params = [agentID,]
    curA.execute(query, params)
    curA.fetchall()

    if (curA.rowcount <= 0):
        print("Relation Not Found")
        curA.fetchall()
        curA.close()
        cnx.close()
        return([])
    elif (curA.rowcount > 0):
        curA = MySQLCursor(cnx)
        query = "SELECT * FROM represents WHERE agentID = %s"
        params = [agentID,]
        curA.execute(query,params)
        dump = curA.fetchall()
        curA.close()
        cnx.close()
        return(dump)

def fetchFieldDB(tableName, fieldName, id):
    cnx = establishConnection()
    query = "SELECT * FROM "
    if(tableName == 'agent'):
        query += 'agent WHERE agentID = %s'
        index = agentFields[fieldName]
    elif(tableName == 'investor'):
        query += 'investor WHERE investor ID = %s'
        index = investorFields[fieldName]
    elif(tableName == 'property'):
        query += 'property WHERE mlsID = %s'
        index = propertyFields[fieldName]
    elif(tableName == 'criteria'):
        query += 'criteria WHERE investorID = %s'
        index = criteriaFields[fieldName]
    else:
        print("Table Not Found. Check Spelling")
        cnx.close()
        return(0)

    curA = MySQLCursor(cnx)
    params = [id,]
    curA.execute(query, params)
    curA.fetchall()

    if (curA.rowcount <= 0):
        print("Relation Not Found. Check ID")
        curA.close()
        cnx.close()
        return(0)
    elif (curA.rowcount > 0):
        curA.close()
        curA = MySQLCursor(cnx)
        params = [id,]
        curA.execute(query, params)
        dump = curA.fetchall()
        attr = dump[0][index]
        curA.close()
        cnx.close()
        return(attr)

def fetchFieldDB2(dump, fieldName):
    if(dump == 0):
        return(0)
    else:
        length = len(dump[0])

    if(length == 5):
        index = agentFields[fieldName]
    elif(length == 4):
        index = investorFields[fieldName]
    elif(length == 8):
        index = propertyFields[fieldName]
    elif(length == 9):
        index = criteriaFields[fieldName]
    else:
        print("Table Not Found. Check Spelling")
        return(0)

    attr = dump[0][index]
    return(attr)

def tester ():
    cnx = establishConnection()
    
    cnx.close()
 
tester()
