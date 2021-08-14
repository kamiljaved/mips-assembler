from a2b import MIPSCompiler
import sys, getopt
import json

def main(argv):
    inputfile = ''
    outputfile = ''
    addressoffset = 0
    log = False
    usage = f'USAGE: {sys.argv[0]} -i <InputFile> -o <OutputFile> (Optional: -a <AddressOffset> -l [output log])'

    try:
        (opts, args) = getopt.getopt(argv,"hi:o:a:l",["ifile=","ofile=","addroff="])
    except getopt.GetoptError:
        print(usage)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(usage)
            sys.exit()
        elif opt == '-l':
            log = True
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        elif opt in ("-a", "--addroff"):
            addressoffset = int(arg)
    
    if inputfile=='' or outputfile=='':
        print(usage)
        sys.exit(2)

    filetext = ''
    with open(inputfile, 'r') as file:
	    filetext = file.read()

    status, verilog_binary, log_data = MIPSCompiler.Assembly2Binary(filetext, startaddress=addressoffset)

    if status==MIPSCompiler.STATUS_COMPILED:
        with open(outputfile, 'w') as file:
            file.write(verilog_binary)
    elif status==MIPSCompiler.STATUS_NOTCOMPILED_WITH_ERRORS:
        errors = verilog_binary
        print("COMPILATION FAILED. Error List:")
        print("--------------------------------")
        for error in errors:
            print(f'  {error}')

    if log:
        log_json = json.dumps(log_data, indent=4, sort_keys=False)
        with open(str(inputfile.split('.')[0]) + '.log.json', 'w') as file:
            file.write(log_json)

    return



if __name__ == '__main__':
    main(sys.argv[1:])