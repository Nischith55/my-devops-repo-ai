from common_routines import *

print ('Executing python script file is:' + str(sys.argv[0]))
print ('The arguments are:'+ str(sys.argv))

sp = str(sys.argv[1]).strip()
# Set the sp secret values in env variables.. Our frameowrk will handle the rest.
set_azure_creds(sp) 
