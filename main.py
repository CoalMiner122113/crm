from doctest import REPORT_ONLY_FIRST_FAILURE
import PySimpleGUI as sg
from db1 import *


## TODO Check for illegal char in register form
## Make sure first and last name only?
## Generate IDs for investors?
## When Agents enter their given IDs, append their city to make it uID nation wide?

def main():
    
    sg.theme('SystemDefaultForReal')

    # All the stuff inside your window.
    layout = [  
                [sg.Button('Register')],
                [sg.Button('Login')],
             ]

    # Create the main Window
    window = sg.Window('Best Project', layout, resizable=True, finalize=True, size=(200,130))
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED: # if user closes window or clicks cancel
            window.close()
            break
    
        if event == 'Register':
            window.close()
            registerWindow()
            break
        if event == 'Login':
            window.close()
            loginWindow()
            break

def registerWindow():

    layout = [  
                [sg.Text("First Name"), sg.InputText()],
                [sg.Text("Last Name"), sg.InputText()],
                [sg.Text("ID"), sg.InputText()],
                [sg.Text("password"), sg.InputText()],
                [sg.Text("Are you an investor or an agent?")],
                [sg.Button('Investor'), sg.Button('Agent')],
                [sg.Button('Submit')]
             ]
    a_i = ''

    # Create the main Window
    window = sg.Window('Best Project', layout, resizable=True, finalize=True)
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED: # if user closes window or clicks cancel
            window.close()
            break
        if event == 'Agent':
            a_i = 'a'
        if event == 'Investor':
            a_i = 'i'
        if event == 'Submit':
            if a_i == 'a':
                addAgentDB(Agent(0, values[0], values[1], values[2], values[3]))
            elif a_i == 'i':
                addInvestorDB(Investor(values[0], values[1], values[2], values[3]))
                investorCriteriaWindow(values[2])
            else:
                print("Please choose whether you are an agent or an investor")
                continue
            window.close()
            loginWindow()
            break

def investorCriteriaWindow(ID):

    layout = [
             [sg.Text("Add criteria")],
             [sg.Text("Costs"), sg.InputText()],
             [sg.Text("Price Limit"), sg.InputText()],
             [sg.Text("IR"), sg.InputText()],
             [sg.Text("mgLength"), sg.InputText()],
             [sg.Text("Cap"), sg.InputText()],
             [sg.Text("CoC"), sg.InputText()],
             [sg.Text("DSR"), sg.InputText()],
             [sg.Text("Price Min"), sg.InputText()],
             [sg.Text("% Down"), sg.InputText()],
             [sg.Button('Save')]
             ]

    window = sg.Window('Best Project', layout, resizable=True, finalize=True)

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED:
            window.close()
            break
        if event == 'Save':
            addCriteriaDB(dumpToCriteria([ID, values[0], values[5], values[6], values[1], values[2], values[4], values[3], values[7], values[8]]))
            window.close()
            break

def loginWindow():

    layout = [  
                [sg.Text("ID"), sg.InputText()],
                [sg.Text("password"), sg.InputText()],
                [sg.Text("Are you logging in as an investor or an agent?")],
                [sg.Button('Investor'), sg.Button('Agent')],
                [sg.Button('Login')]
             ]
    a_i = ''

    # Create the main Window
    window = sg.Window('Best Project', layout, resizable=True, finalize=True)
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED: # if user closes window or clicks cancel
            window.close()
            break
        if event == 'Agent':
            a_i = 'a'
            agent = fetchAgentDB(values[0], values[1])
            if(len(agent) == 0):
                print("Account Not Found, Please Try Again.")
                continue
        if event == 'Investor':
            a_i = 'i'
            investor = fetchInvestorDB(values[0], values[1])
            if(len(investor) == 0):
                print("Account Not Found, Please Try Again.")
                continue
        if event == 'Login':
            if a_i == 'a':
                window.close()
                mainWindowAgent(agent, [])
                break
            elif a_i == 'i':
                window.close()
                mainWindowInvestor(investor, [])
                break
            else:
                print("Please choose whether you are logging in as an agent or an investor")
                continue

def mainWindowInvestor(investor, rows):
    layout = [
                [sg.Text("Enter City"), sg.InputText(), sg.Text("Enter State"), sg.InputText(), sg.Button("Search"), sg.Button("Change/View Criteria")],
                [sg.Text("MLS ID"), sg.Text("Price"), sg.Text("SqFt"), sg.Text("Rent"), sg.Text("Address"), sg.Text("City"), sg.Text("Subzone"), sg.Text("Cap%"), sg.Text("CoC%"), sg.Text("DSR")]
             ]
    for row in rows:
        layout.append(row)
    
    window = sg.Window('Best Project', layout, resizable=True, finalize=True)

    while True:
        event, values = window.read()
        dump = fetchCriteriaDB(investor[0][0])
        crit = dumpToCriteria(dump[0])
        if(event == 'Change/View Criteria'):
            window.close()
            mainWindowInvestor(investor, [
                [sg.Text("Please update the following criteria:")],
                [sg.Text("\t\tCurrent\t\tNew")],
                [sg.Text("Costs:\t\t"), sg.Text(crit.costs), sg.InputText()],
                [sg.Text("Price Limit:\t"), sg.Text(crit.lim), sg.InputText()],
                [sg.Text("IR:\t\t"), sg.Text(crit.ir), sg.InputText()],
                [sg.Text("mgLength:\t"), sg.Text(crit.mgLen), sg.InputText()],
                [sg.Text("Cap:\t\t"), sg.Text(crit.cap), sg.InputText()],
                [sg.Text("CoC:\t\t"), sg.Text(crit.coc), sg.InputText()],
                [sg.Text("DSR:\t\t"), sg.Text(crit.dsr), sg.InputText()],
                [sg.Text("Price Min:\t"), sg.Text(crit.min), sg.InputText()],
                [sg.Text("% Down:\t\t"), sg.Text(crit.down), sg.InputText()],
                [sg.Button('Save')]
            ])
            break
        if(len(dump)==0):
            print("Criteria Invalid. Please Update.")
            continue
        if(event == 'Search'):
            city = values[0]   
            if(len(fetchHouseByCityDB(city))==0):
                print("No houses in area")
                continue
            rows = []
            houseList = fetchHouseByCityDB(city)
            for house in houseList:
                house = dumpToHouse(house)
                cap = calCap(house, crit)
                dsr = calDSR(house, crit)
                row = [sg.Text(house.mlsID), sg.Text(house.price), sg.Text(house.sqft), sg.Text(house.rent), sg.Text(house.address), sg.Text(house.city), sg.Text(house.sZone), sg.Text(cap), sg.Text("CoC%"), sg.Text(dsr)]
                rows.append(row)
            window.close()
            mainWindowInvestor(investor, rows)
            break
        if(event == 'Save'):
            updateCriteriaDB(dumpToCriteria([investor[0][0], values[2], values[7], values[8], values[3], values[4], values[6], values[5], values[9], values[10]]))
            window.close()
            mainWindowInvestor(investor, [])
            break

def mainWindowAgent(agent, rows):

    layout = [
                [sg.Text("Enter City"), sg.InputText(), sg.Text("Enter State"), sg.InputText(), sg.Button("Search"), sg.Button("View/Add Investors")],
                [sg.Text("MLS ID"), sg.Text("Price"), sg.Text("SqFt"), sg.Text("Rent"), sg.Text("Address"), sg.Text("City"), sg.Text("Subzone")]
             ]

    for row in rows:
        layout.append(row)
    
    window = sg.Window('Best Project', layout, resizable=True, finalize=True)

    while True:
        event, values = window.read()

        if(event == 'View/Add Investors'):
            rows = [
                [sg.Text("Enter Investor ID: "), sg.InputText(), sg.Button('Add'),sg.Button('Back To Properties')],
                [sg.Text("Investors")]
            ]
            repList = fetchRepByAgentDB(agent[0][0])
            for rep in repList:
                investor2 = fetchInvestorDB2(rep[1])
                investor2 = dumpToInvestor(investor2[0])
                row = [sg.Text(investor2.fName),sg.Text(investor2.lName)]
                rows.append(row)

            window.close()
            mainWindowAgent(agent,rows)
            break
        if(event == 'Add'):
            agent1 = dumpToAgent(agent[0])
            investor1 = fetchInvestorDB2(values[2])
            if(len(investor1)==0):
                print("Investor Not Found.")
                continue
            investor1 = dumpToInvestor(investor1[0])
            addRepDB(agent1, investor1)
        if(event == 'Back To Properties'):
            window.close()
            mainWindowAgent(agent[0], [])
            break
        if(event == 'Search'):
            city = values[0]   
            if(len(fetchHouseByCityDB(city))==0):
                print("No houses in area")
                continue
            rows = []
            houseList = fetchHouseByCityDB(city)
            for house in houseList:
                house = dumpToHouse(house)
                row = [sg.Text(house.mlsID), sg.Text(house.price), sg.Text(house.sqft), sg.Text(house.rent), sg.Text(house.address), sg.Text(house.city), sg.Text(house.sZone)]
                rows.append(row)
            window.close()
            mainWindowAgent(agent, rows)
            break


if __name__ == "__main__":
    main()