# Write up - too lazy to write
def main():
    # 1
    MU = 1
    print("\t\t\t******** Write up *********")
    print("*----------------------------------------------------------------------*")
    print("|                    Utilization = rho = lambda/mu                     |")
    print("|                    Mean Queue Length = rho/(1-rho)                   |")
    print("*----------------------------------------------------------------------*")
    
    for lamb in [0.1, 0.25, 0.4, 0.55, 0.65, 0.80, 0.90]:
        rho = lamb / MU
        my_mql = rho/(1-rho)
        print("MU = 1, Lambda = " + str(lamb))
        print("Server Utilization = " + str(lamb) + "/" + str(MU) + " = " + str(rho))
        print("Mean Queue Length = " + str(rho) + "/" + "(1-" + str(rho) + ") = " + str(my_mql) + "\n")
               
main()
