import argparse 
import RoundRobin as RR

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", help="Mostrar información de depuración", action="store_true")
parser.add_argument("-n", "--numberOfProcess", help="Numero de procesos")
parser.add_argument("-q", "--quantum", help="Numero de procesos")
args = parser.parse_args()

n = int(args.numberOfProcess)
q = int(args.quantum)

RR.main(n,q)