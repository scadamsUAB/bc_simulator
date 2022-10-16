import time
import json
from pqcrypto.sign.falcon_512 import sign, verify, generate_keypair
from IPFSCallHelper import IPFSWorker
import random
import string
import base64
import copy
### load current committee into memory
members = []
#f = open("conf/comitteeNodes.json")
#content = f.read()
#f.close()
#committee = json.loads(content)
#print("COMMITTEE", committee)
#for m in committee["members"]:  
#    members.append(m["address"])
#print("MEMBERS", members)
## Meta Genesis: QmcUspFPs4nziiLmSm2jRume73jWv9R3nYETC7hLvcS5jX.json
## SupportFiles/MetaGenesisSource.json
## Default values
## initial blank state: QmbJWAESqCsf4RFCqEY7jecCashj8usXiyDNfKtZCwwzGb
current_height = 0
ipfshttphelper = IPFSWorker()
random.seed(10)
meta_genesis = "QmcUspFPs4nziiLmSm2jRume73jWv9R3nYETC7hLvcS5jX"
block_genesis ="QmZJhTkdvVCQyPFez7XQYENxC4rYvS8tqYSzEzzneCfksK"
validation_genesis="QmTaxJNFCMj8YBHVG3AX3uACLnu24jgTBryUJMKwn9kbpP"

signature = "390e9292d04d38d6a7e6225e442110fdfbe1fa2889af97288a5eb39cd9d7a97dfc62c33e7294f3560c845c194d8a239779ba5537ce4527d8bb3a36be999a8f0b26066fcf418bf67b6b25df5bd5543a0ec12b69f1cc48f0f82363c93cad550c836f92fa7d0e29d5c9b2da59da4c582b9dea131aae3085b6eaeaf77fce9ee6ed96de4bca5babb32cf8bf8b9d7568130ca30aec3d2b9d9270cb842c63244e3d5252b11194846c242492b8e145c48950441313bfb64212a92d53fd8dfcd86d508693bcc7a8b59b0ee95acc3a24bf45187550c80e8183204cc4c159b7b71ebab22500429ba879e624cca1c37051c40d964d7f64c735ab223a27c3cd7ab428bc5916334426032095772d67c5fa6f627e723ed793e674db77adb7b49587d6aa0e35b9a5d375b9533b3cffa70433467a99b460f42dc98bbfb82542bdfc572794ac451598dfe654f32f22ac59af6c8f6f0ea6f22954f5e3649f731177bdbe691e1e9ed9a03bfcf937b2c179cd6fcf0e0111226a6d28c3d4183183e7168abc022b7346c9810580469cb872c4554569268dd53a55b476a12a36f914cf4f08e8b4c67eb67c99e1a0d45d8fed9d39d1e09956192293eb1d831d85757d2f3f6a870cd7c9b79bfc5daed35f611395ad11b9e2dd1421a9d866f111676fb2df1c96599b8dbfece1ad9de715c4a2913d8ee21e0c12e8dbb299a3c3a5a7431ae7d26314d335280221cb7c290b39238f88d3b742d748a0bf74e692f7eab104f6453eaa9fa4e5e28d30ef4edda62fac43737962585a0735f4cebbf276f669d6813512f83126433b1a4b2b522e0d7a733b7e9217cccc23ddacdc0884ea3a4dfcbf456bb8a5e2c0c6db9087f6785a90f43f6d9f21d56848ce44530f9f70b4ac118d0308af64392dec2656860d81a463eadb7254c7308c298430f07fdaa5c940"

log_filename ="SupportFiles/log.txt" 
f = open(log_filename,"w")
f.write("STARTING NEW LOG\n")
f.close()

f = open("SupportFiles/blocks.txt","w")
f.close()

################
##### TESTING FUNCTIONS

#### TESTING ONLY
def set_behavior():
    f = open("SupportFiles/addresses.txt")
    addresses = f.readlines()
    f.close()
    account_behavior={}
    for a in addresses:
        account_behavior[str(a.strip())]=0
    f = open("SupportFiles/behavior.json","w")
    f.write(json.dumps(account_behavior))
    f.close()    

#### TESTING ONLY
def load_behavior():
    f = open("SupportFiles/behavior.json")
    behaviors = f.read()
    f.close()
    behaviors = json.loads(behaviors)
    print(behaviors)
    return behaviors

#### TESTING ONLY
def create_fake_cid():
# printing letters
    letters = string.ascii_letters

    x=''.join(random.choice(letters) for i in range(10))
    f = open("SupportFiles/temp.txt","w")
    f.write(x)
    f.close()
    return(ipfshttphelper.getCID("SupportFiles/temp.txt"))


#### TESTING ONLY??
def initialize_account_state():
    x = {}
    y = json.dumps(x)
    print("INITIALIZE ACCOUNT STATE",y)
    f = open("SupportFiles/temp.txt","w")
    f.write(y)
    f.close()
    return(ipfshttphelper.getCID("SupportFiles/temp.txt"))

#### TESTING ONLY??
def initialize_reward_state():
    x = {}
    y = json.dumps(x)
    print("INITIALIZE REWARD STATE",y)
    f = open("SupportFiles/temp.txt","w")
    f.write(y)
    f.close()
    return(ipfshttphelper.getCID("SupportFiles/temp.txt"))


##### TESTING ONLY


def initialize_initial_committee(): 
    users = []
    user ={}
    user["address"] = "QmcCLC5cUdXQ9EdSkoGcVY7UPxiU4VHB43YNtwjXYFvgMR"
    user["server"] = "3.13.252.251,8000"
    user["ipfs"] = "12D3KooWDMFk1dfWeNCeeYCssyXcDbNBv8WTEKScEmG4WxNBXnvY"
    users.append(user)
    selections["QmcCLC5cUdXQ9EdSkoGcVY7UPxiU4VHB43YNtwjXYFvgMR"] = 1
    print()
    print(users)
    f = open("SupportFiles/temp.txt","w")
    f.write(json.dumps(user))
    f.close()

    a = ipfshttphelper.addFileByPath("SupportFiles/temp.txt")
 
    

    f = open("SupportFiles/accounts.txt")
    values = f.readlines()
    f.close()
    cleaned_values = []
    
    for v in values:
        cleaned_values.append(v.strip())
    print("VALUES: ", cleaned_values)

    if a.replace("\n","") in cleaned_values:
        print("INITIAL COMMITTEE MEMBER ALREADY ADDED")
    else:
        f = open("SupportFiles/accounts.txt","a")
        f.write(a)
        f.write("\n")
        f.close()


        f = open("SupportFiles/addresses.txt","a")
        f.write(user["address"])
        f.write("\n")
        f.close()

    user ={}
    user["address"] = "QmRS2GA8ZPZa6jokcbUh3aVeRCXqBoKRksTfh1kNMQoDSp"
    user["server"] = "3.136.166.197,8000"
    user["ipfs"] = "12D3KooWH1sdCP1WuK9miYqX39V89Xr1erNCsCJK26GCGAmc7ZmB"
    users.append(user)
 
    selections["QmRS2GA8ZPZa6jokcbUh3aVeRCXqBoKRksTfh1kNMQoDSp"] = 1
    print()
    print(users)
    f = open("SupportFiles/temp.txt","w")
    f.write(json.dumps(user))
    f.close()

    a = ipfshttphelper.addFileByPath("SupportFiles/temp.txt")

    

    f = open("SupportFiles/accounts.txt")
    values = f.readlines()
    f.close()

    if a.replace("\n","") in cleaned_values:
        print("INITIAL COMMITTEE MEMBER ALREADY ADDED")
    else:
        f = open("SupportFiles/accounts.txt","a")
        f.write(a)
        f.write("\n")
        f.close()


        f = open("SupportFiles/addresses.txt","a")
        f.write(user["address"])
        f.write("\n")
        f.close()
    user ={}

    user["address"] = "QmP2ZFpNFHhBYrRWYoVfzQVUYJNCHYdfozyvkZGTvbmdXG"
    user["server"] = "3.136.193.247,8000"
    user["ipfs"] = "12D3KooWKuJ2Z7eXFmtuu8wonokG2bc9Fe923vNaR3xhxNVqFShU"
    users.append(user)
    selections["QmP2ZFpNFHhBYrRWYoVfzQVUYJNCHYdfozyvkZGTvbmdXG"] = 1
 

    f = open("SupportFiles/temp.txt","w")
    f.write(json.dumps(user))
    f.close()

    a = ipfshttphelper.addFileByPath("SupportFiles/temp.txt")


    f = open("SupportFiles/accounts.txt")
    values = f.readlines()
    f.close()

    if a.replace("\n","") in cleaned_values:
        print("INITIAL COMMITTEE MEMBER ALREADY ADDED")
    else:
        f = open("SupportFiles/accounts.txt","a")
        f.write(a)
        f.write("\n")
        f.close()


        f = open("SupportFiles/addresses.txt","a")
        f.write(user["address"])
        f.write("\n")
        f.close()


    members ={}
    members["members"] = users
    print()
    print()
    print(users)
    f = open("SupportFiles/temp.txt","w")
    f.write(json.dumps(members))
    f.close()

    ### LOAD COMMITTEE FILE
    f = open("SupportFiles/currentCommittee.txt","w")
    f.write("QmcCLC5cUdXQ9EdSkoGcVY7UPxiU4VHB43YNtwjXYFvgMR\n")
    f.write("QmRS2GA8ZPZa6jokcbUh3aVeRCXqBoKRksTfh1kNMQoDSp\n")
    f.write("QmP2ZFpNFHhBYrRWYoVfzQVUYJNCHYdfozyvkZGTvbmdXG\n")
    f.close()

    a = ipfshttphelper.addFileByPath("SupportFiles/temp.txt")

    print("INITIAL COMMITTEE", a)
    return a

def initialize_initial_committee_updated(): 
    f = open("SupportFiles/initcomitteeNodes.json")
    content = f.read()
    f.close()
    users = []
    content = json.loads(content)
    members = content["members"]
    f = open("SupportFiles/currentCommittee.txt","w")
    f.close()
    for m in members:

      #  m = json.loads(m)
    #  user ={}
    #  user["address"] = "QmcCLC5cUdXQ9EdSkoGcVY7UPxiU4VHB43YNtwjXYFvgMR"
    #  user["server"] = "3.13.252.251,8000"
    #  user["ipfs"] = "12D3KooWDMFk1dfWeNCeeYCssyXcDbNBv8WTEKScEmG4WxNBXnvY"

 
        users.append(m)
        selections[m["address"]] = 1
        #print()
        #print(users)
        f = open("SupportFiles/temp.txt","w")
        f.write(json.dumps(m))
        f.close()

        a = ipfshttphelper.addFileByPath("SupportFiles/temp.txt")
        address_to_account[str(m["address"]).strip()] = str(a).strip()
        account_to_address[str(a).strip()] = str(m["address"]).strip()

    

        f = open("SupportFiles/accounts.txt")
        values = f.readlines()
        f.close()
        cleaned_values = []
        
        for v in values:
            cleaned_values.append(v.strip())
        #print("VALUES: ", cleaned_values)

        if a.replace("\n","") in cleaned_values:
            print("INITIAL COMMITTEE MEMBER ALREADY ADDED")
        else:
            f = open("SupportFiles/accounts.txt","a")
            f.write(a)
            f.write("\n")
            f.close()


            f = open("SupportFiles/addresses.txt","a")
            f.write(m["address"])
            f.write("\n")
            f.close()
      
        f = open("SupportFiles/currentCommittee.txt","a")
        f.write(m["address"]+"\n")
        f.close()
    members ={}
    members["members"] = users
    print()
    print()
    print(users)
    f = open("SupportFiles/temp.txt","w")
    f.write(json.dumps(members))
    f.close()

    ### LOAD COMMITTEE FILE
  #  f = open("SupportFiles/currentCommittee.txt","w")
  #  f.write("QmcCLC5cUdXQ9EdSkoGcVY7UPxiU4VHB43YNtwjXYFvgMR\n")
  #  f.write("QmRS2GA8ZPZa6jokcbUh3aVeRCXqBoKRksTfh1kNMQoDSp\n")
  #  f.write("QmP2ZFpNFHhBYrRWYoVfzQVUYJNCHYdfozyvkZGTvbmdXG\n")
  # f.close()

    a = ipfshttphelper.addFileByPath("SupportFiles/temp.txt")

    print("INITIAL COMMITTEE", a)
    return a, len(members["members"])

#### TESTING ONLY
def generate_user():
    public_key, secret_key = generate_keypair()
    ## CONVERT KEY BYTES TO BASE64 THEN TO ASCII STRING
    b64PubKey=base64.encodebytes(public_key)
    asciiPubKey=b64PubKey.decode('utf-8')
    ## UPLOAD THE PUBLIC KEY FILE TO IPFS
    pubAddress=ipfshttphelper.addfile(asciiPubKey,"PK")
    return secret_key,pubAddress



#### TESTING ONLY
def initialize_account_users(count):
    account_to_address ={}
    address_to_account ={}

    f = open("SupportFiles/accounts.txt","w")
    f.close()
    f = open("SupportFiles/addresses.txt","w")
    f.close()
    for i in range(0,count):
        user ={}
        priv, user_address = generate_user()
        print("USER ADDRESS   ", user_address)
        user["address"] = user_address
        user["server"] = "3.13.252.251,8000"
        user["ipfs"] = "12D3KooWDMFk1dfWeNCeeYCssyXcDbNBv8WTEKScEmG4WxNBXnvY"
        f = open("SupportFiles/temp.txt","w")
        f.write(json.dumps(user))
        f.close()

        a = ipfshttphelper.addFileByPath("SupportFiles/temp.txt")
      

        f = open("SupportFiles/accounts.txt","a")
        f.write(a)
        f.write("\n")
        f.close()


        f = open("SupportFiles/addresses.txt","a")
        f.write(user_address)
        f.write("\n")
        f.close()
        account_to_address[str(a).strip()] = str(user_address).strip()
        address_to_account[str(user_address).strip()] = str(a).strip()
    
    f = open("SupportFiles/account_to_address.json","w")
    f.write(json.dumps(account_to_address))
    f.close()

    f = open("SupportFiles/address_to_account.json","w")
    f.write(json.dumps(address_to_account))
    f.close()

### HELPER FUNCTION TO GET TEXT FROM CID
def get_text_content_from_ipfs(CID):
    CID = CID.replace("\n","")
    content = ipfshttphelper.getContent(CID,"NA")
    try: 
        content = content.decode("UTF-8")
    except:
        pass
    return content


def clear_pending():
    f = open("SupportFiles/pending.txt","w")
    f.close()


def get_reward_state(CID):
    content = get_text_content_from_ipfs(CID)
    print("REWARD STATE",content)

    

def should_add_member(modifier, score):
    modified_score = 100 + modifier + score
    modified_baseline = 100 + modifier
    target = (modified_baseline *3)//4

    return random_chance(modified_score, target)


def new_committee_select(modifier, reward_state_CID):
    reward_state = get_text_content_from_ipfs(reward_state_CID)
    reward_state = json.loads(reward_state)
  
    f = open("SupportFiles/pending.txt")
    pending = f.readlines()
    f.close()
    cleaned_pending =[]
  
    for p in pending:
        if len(p.strip())==46:
            cleaned_pending.append(p.strip())
    selected = []

#    print("&&&&&&&&&&",cleaned_pending,len(cleaned_pending))
    while len(selected) < committee_size:
 #       print("SIZE OF CLEAR PENDING: ",len(cleaned_pending))
        index = random.randint(0,len(cleaned_pending)-1)
  #      print("INDEX: ", index)
        if index in selected:
            print("ALREADY SELECTED")
           # pass
        else:
            addr = get_text_content_from_ipfs(cleaned_pending[index])
            addr = json.loads(addr)
            addr = addr["address"]
            score = 0
            if addr in reward_state:
 #               print("IN STATE: ")
                score = reward_state[addr.replace("\n","")]
            else:
  #              print("NOT IN STATE: ")
                score = 0
            should_add = should_add_member(modifier, score)
            if should_add:
                selected.append(index)
    print("SELECTED INDEXES: ", selected)
    new_users = []

    for user in selected:
        usercid = pending[user]
       
        usercid = usercid.replace("\n","")
 #       print("USERCID: ",usercid, len(usercid))
        content = get_text_content_from_ipfs(usercid)
        content = json.loads(content)
 #       print("CONTENT: ", content, type(content))
        new_users.append(content)
   
    f = open("SupportFiles/currentCommittee.txt","w")
    f.close()
    new_addresses = []
   
    
    for nu in new_users:
        new_addresses.append(nu["address"].strip())
    f = open("SupportFiles/currentCommittee.txt","a")
    for na in new_addresses:
        f.write(na+"\n")
    f.close()
   
    members ={}
    members["members"] = new_users
 #   print("******************")
 #   print("MEMBERS:::::", members)
    f = open("SupportFiles/temp.txt","w")
    f.write(json.dumps(members))
    f.close()
    new_committee_CID = ipfshttphelper.addFileByPath("SupportFiles/temp.txt")
#    print("NEW COMMITTEE CID = ", new_committee_CID)
    clear_pending()
    return new_committee_CID


    
def get_average_score_modifier(CID, reward_state):
    reward_state = get_text_content_from_ipfs(reward_state)
    try:
        reward_state  = json.loads(reward_state)
    except:
        pass

    content = get_text_content_from_ipfs(CID)
    members = content.split("\n")
    scores=[]
    for m in members:

        if len(m) == 46:
            if m in reward_state:
                scores.append(reward_state[m])
            else:
                scores.append(0)

           # content = get_text_content_from_ipfs(m)
    return  get_modifier_value(scores)
    
def get_modifier_value(values):
    ### REMOVE NEGATIVE VALUES
    values = [x for x in values if x >=0]
 #   print("GETTING MODIFIER VALUES:",values)

    ### SORT THE LIST
    sorted_values = sorted(values)

    #### REMOVE TOP 1/4 OF VALUES
    list_length = len(sorted_values)
    sorted_values = sorted_values[0:((3*list_length)//4)]
    if len(sorted_values) ==0:
        return 0

    #### CALCULATE THE AVERAGE BASED ON REMAINING VALUES
    average = sum(sorted_values) // len(sorted_values)
 #   print("AVERAGE", average)
    return average

 #   print("new sorted values: ", sorted_values)


def reward_member(account_state,account_id):
    if account_id in account_state:
        account_state[account_id] = account_state[account_id] + 1
    else:
        account_state[account_id] = 1

    return account_state

def penalize_member(account_state, account_id):
    if account_id in account_state:
        account_state[account_id] = account_state[account_id] - 1
    else:
        account_state[account_id] = -1
    return account_state

def update_accout_state(account_state, members, honest_array):
    account_state_content = ipfshttphelper.getContent(account_state,"NA")
    try:
        account_state_content = account_state_content.decode('UTF-8')
    except:
        pass
    
    try:
        account_state_object = account_state_content()
    except:
        account_state_object = json.loads(account_state_content)
    for i in range(0, len(members)):
        if honest_array[i] == True:
            account_state_object = reward_member(account_state_object,members[i].replace("\n",""))
        else:
            account_state_object =  penalize_member(account_state_object,members[i].replace("\n",""))
    
    account_state_content = json.dumps(account_state_object)
    f = open("SupportFiles/temp.txt","w")
    f.write(account_state_content)
    f.close()
    return ipfshttphelper.addFileByPath("SupportFiles/temp.txt")

def update_accout_state_old(account_state, members, member1=True,member2=True,member3=True):
    account_state_content = ipfshttphelper.getContent(account_state,"NA")
    try:
        account_state_content = account_state_content.decode('UTF-8')
    except:
        pass
    
    try:
        account_state_object = account_state_content()
    except:
        account_state_object = json.loads(account_state_content)

    if member1 == True:
       account_state_object = reward_member(account_state_object,members[0].replace("\n",""))
    else:
       account_state_object =  penalize_member(account_state_object,members[0].replace("\n",""))
    

    if member2 == True:
        account_state_object = reward_member(account_state_object, members[1].replace("\n",""))
    else:
        account_state_object = penalize_member(account_state_object,members[1].replace("\n",""))
        

    if member3 == True:
        account_state_object = reward_member(account_state_object,members[2].replace("\n",""))
    else:
        account_state_object = penalize_member(account_state_object,members[2].replace("\n",""))
    account_state_content = json.dumps(account_state_object)
    f = open("SupportFiles/temp.txt","w")
    f.write(account_state_content)
    f.close()

    return ipfshttphelper.addFileByPath("SupportFiles/temp.txt")

def update_reward_state(reward_state, members, honest_array):
    reward_state_content = ipfshttphelper.getContent(reward_state,"NA")
    try:
        reward_state_content = reward_state_content.decode('UTF-8')
    except:
        pass
    
    try:
        reward_state_object = reward_state_content()
    except:
        reward_state_object = json.loads(reward_state_content)
    for i in range(0, len(members)):
        if honest_array[i] == True:
            reward_state_object = reward_member(reward_state_object,members[i].replace("\n",""))
        else:
            reward_state_object =  penalize_member(reward_state_object,members[i].replace("\n",""))
    
    reward_state_content = json.dumps(reward_state_object)
    f = open("SupportFiles/temp.txt","w")
    f.write(reward_state_content)
    f.close()
    return ipfshttphelper.addFileByPath("SupportFiles/temp.txt")

def update_reward_state_old(reward_state, members, member1=True,member2=True,member3=True):
    reward_state_content = ipfshttphelper.getContent(reward_state,"NA")
    try:
        reward_state_content = reward_state_content.decode('UTF-8')
    except:
        pass
    
    try:
        reward_state_object = reward_state_content()
    except:
        reward_state_object = json.loads(reward_state_content)

    if member1 == True:
       reward_state_object = reward_member(reward_state_object,members[0].replace("\n",""))
    else:
       reward_state_object =  penalize_member(reward_state_object,members[0].replace("\n",""))
    

    if member2 == True:
        reward_state_object = reward_member(reward_state_object, members[1].replace("\n",""))
    else:
        reward_state_object = penalize_member(reward_state_object,members[1].replace("\n",""))
        

    if member3 == True:
        reward_state_object = reward_member(reward_state_object,members[2].replace("\n",""))
    else:
        reward_state_object = penalize_member(reward_state_object,members[2].replace("\n",""))
    reward_state_content = json.dumps(reward_state_object)
    f = open("SupportFiles/temp.txt","w")
    f.write(reward_state_content)
    f.close()

    return ipfshttphelper.addFileByPath("SupportFiles/temp.txt")



def load_committee():
    f = open("SupportFiles/currentCommittee.txt")
    members = f.readlines()
    f.close()
    return members


def update_log(block_CID, reward_state_CID,previous_meta_CID, old_committee_CID, new_committee_CID ):
    entry={}
    entry["blockCID"] = block_CID
    entry["rewardStateCID"]= reward_state_CID
    entry["previousMetaCID"] = previous_meta_CID
    entry["previousCommitteeCID"] = old_committee_CID
    entry["newCommitteeCID"] = new_committee_CID

    log_entries.append(entry)
    content = get_text_content_from_ipfs(new_committee_CID)
    content = json.loads(content)
    members = content["members"]
    for m in members:
        addr = m["address"].replace("\n","") 
        if addr in selections:
            selections[addr]= selections[addr] +1
        else:
            selections[addr] = 1



    


def random_chance(upper_range,threshold):
    
    if upper_range < threshold:
        return False
    number = random.randint(0,upper_range)
    if number >= threshold:
        return True
    print(number,threshold, upper_range)
    return False

def add_pending_member():
    pending = []
    pending = copy.copy(accounts_full)
    #should_add = random_chance(10,0)
    #print("in add_pending_member", should_add)
    ### GET CURRENT COMMITTEE
    f = open("SupportFiles/currentCommittee.txt")
    current_committee = f.readlines()
    f.close()
    cleaned_current_committee =[]
    for cc in current_committee:
        #cleaned_current_committee.append(cc.strip())
        print("removing", cc)
        print((address_to_account[cc.strip()]))
        pending.remove(address_to_account[[cc.strip()]])
        
#    for a in accounts_full:
#        content = get_text_content_from_ipfs(str(a).strip())
#        content = json.loads(content)
#        if content["address"].replace("\n","") in cleaned_current_committee:
#            print("In Current Committee",content["address"])
#        else:
       
#    for a in accounts_full:
#        content = get_text_content_from_ipfs(str(a).strip())
#        content = json.loads(content)
#        if content["address"].replace("\n","") in cleaned_current_committee:
#            print("In Current Committee",content["address"])
#        else:
#            pending.append(str(a).strip())
    print("Start Writing pending")

    with open(r"SupportFiles/pending.txt","w") as f:
        f.write("\n".join(pending))

    j = input("PAUSE")     
 #   f=open("SupportFiles/pending.txt","w")
 #   for line in pending:
 #       print(len(line),line)
 #       if len(line)==46:
 #           f.write(str(line)+"\n")
 #       else:
 #           print("ERROR WRITING")
 #   f.close()
    print("DONE WRITING PENDING")

   # if should_add == True:
   #     print("SHOULD ADD")
   #     f = open("SupportFiles/pending.txt")
   #     pending = f.readlines()
   #     f.close()
   #     print("READ PENDING FILE")

   #     print("*************************")
   #     print("PENDING: ")
   #     print(pending)
   #     print("*****************************")
    #    f = open("SupportingFiles/addresses.txt")
    #    addresses = f.readlines()
    #    f.close()
    #    print("READING ACCOUNTS")
    #    f = open("SupportFiles/accounts.txt")
    #    accounts = f.readlines()
    #    f.close()
    #    print("DONE READING ACCOUNTS")
    #    added_count = 0
    #    while added_count < should_add_count:
    #        print("IN loop",added_count,should_add_count)
    #        added = False
    #        while added ==False:
#
#                if len(pending) < total_addresses:
#                    selected_index = random.randint(0,len(accounts)-1)
#
#                    if accounts[selected_index] in pending: 
#                        print("ACCOUNT IN PENDING")
#                   #     pass
#                    else:
#                        ### ADDRESS CHECK
#                        print("CHECKING ADDRESS")
#                        content = get_text_content_from_ipfs(accounts[selected_index])
#                        content = json.loads(content)
#                        if  content["address"].replace("\n","") in cleaned_current_committee:
#                            print("IN CURRENT COMMITTEE")
#
#                    #        pass
##                        else:
#                            pending.append(accounts[selected_index])
#                            print("START WRITING TO PENDING")
#                            f = open("SupportFiles/pending.txt","w")
#                            for line in pending:
#                                if len(line) ==47:
#                                    f.write(line)
#                            f.close()
#                            print("DONE WRITING PENDING")
#                            added = True
#                            added_count = added_count + 1 
#    return ipfshttphelper.addFileByPath("SupportFiles/pending.txt")

def createMetaBlock(previous_meta_id, previous_meta_height, previous_block_id, previous_val_id,  account_state, reward_state, committee_id):
    should_update_log = False
    new_block = {}
    block_data = {}

    current_timestamp = time.time()
    block_height = previous_meta_height + 1

    block_data["Timestamp"] = current_timestamp
    block_data["Height"] = block_height  
    blockRef = create_fake_cid()
    validationRef = create_fake_cid()
    block_data["BlockRef"] = blockRef
    block_data["ValidationRef"]=validationRef
    if(previous_meta_id ==""):
        block_data["PreviousMetaBlock"]= meta_genesis
    else:
        block_data["PreviousMetaBlock"] = previous_meta_id
    
    if(previous_block_id ==""):
        block_data["PreviousBlock"]= block_genesis
    else:
        block_data["PreviousBlock"] = previous_block_id
    
    if(previous_val_id ==""):
        block_data["PreviousBlock"]= validation_genesis
    else:
        block_data["PreviousValidation"] = previous_block_id

    committee_detail = get_text_content_from_ipfs(committee_id)
    committee_detail = json.loads(committee_detail)
    behaviors_array = []
#    behavior_1 = behaviors[committee_detail["members"][0]["address"]]
#    behavior_2 = behaviors[committee_detail["members"][1]["address"]]
#    behavior_3 = behaviors[committee_detail["members"][2]["address"]]

    members = load_committee()
    random.seed(previous_meta_id)
 #   a = input(members)
    print("Checking Members")
    for m in members:
        mem = m.strip()
        behaviors_array.append(random_chance(100,behaviors[mem]))
       
 #   member1_honest = random_chance(100,behavior_1)
   # print("MEMBER 1 honest", member1_honest)
#    member2_honest = random_chance(100,behavior_2)
   # print("MEMBER 2 honest", member2_honest)
 #   member3_honest = random_chance(100,behavior_3)
 #   print("HONEST MEMBERS", member1_honest, member2_honest, member3_honest)
  #  x = input(behaviors_array)
    
    new_account_state = update_accout_state(account_state,members,behaviors_array)
    new_reward_state = update_reward_state(reward_state,members,behaviors_array)

    block_data["AccountState"] = new_account_state
    block_data["RewardState"] = new_reward_state
    if(block_height +1)%10 == 2:
    
        print("ADDING PENDING MEMBER")
        add_pending_member()
    pending_id = ipfshttphelper.addFileByPath("SupportFiles/pending.txt")
    block_data["PendingMembers"] = pending_id

   #### TESTING FOR VALUES WITH CURRENT COMMITTEE 
  #  get_average_score_modifier("QmWLt1NnzKVaDErbfSFTCcdgQfDPBEA1A7BKtZacimfihu", new_reward_state)

    print("CURRENT BLOCK HEIGHT ", block_height)
    if (block_height + 1 )% 10 == 0:
        ## NEW COMMITTEE
        print()
        print()
        print("NEW COMMITTEE SELECTION")
        pending_id = block_data["PendingMembers"]

        modifier = get_average_score_modifier(pending_id, new_reward_state)

        new_committee_CID = new_committee_select(modifier, new_reward_state)
        block_data["NextCommitteeID"] = new_committee_CID
        should_update_log = True
    else:

        block_data["NextCommitteeID"] = committee_id
        new_committee_CID = committee_id

    block_data["CommitteeID"] = committee_id
    new_block["Data"] = block_data
    new_block["Signature"] = signature

    block_content = json.dumps(new_block)
    f = open("SupportFiles/temp.txt","w")
    f.write(block_content)
    f.close()

    cid = ipfshttphelper.addFileByPath("SupportFiles/temp.txt")
    
    f = open("SupportFiles/blocks.txt","a")
    f.write(cid+"\n")
    f.close()
    if should_update_log:
        update_log(cid,new_reward_state,previous_meta_id,committee_id,new_committee_CID)

    return cid, block_height, blockRef, validationRef, new_account_state, new_reward_state, new_committee_CID
'''
{    
"Data": 
	{
	"Timestamp": 1640995202.0, 
	"Height": 0, "Miner": "QmaHx8iHzKWMx4mGsPstPFcE4xnViuzLzJQ6NvhfuoLst7", 
	"BlockRef": "QmZJhTkdvVCQyPFez7XQYENxC4rYvS8tqYSzEzzneCfksK", 
	"ValidationRef": "QmTaxJNFCMj8YBHVG3AX3uACLnu24jgTBryUJMKwn9kbpP", 
	"PreviousMetaBlock": null, 
	"PreviousBlock": null, 
	"PreviousValidation": null, 
	"AccountState": "QmfSnGmfexFsLDkbgN76Qhx2W8sxrNDobFEQZ6ER5qg2wW", 
	"RewardState": "QmfSnGmfexFsLDkbgN76Qhx2W8sxrNDobFEQZ6ER5qg2wW", 
	"PendingMembers":
    
    "CommitteeID": "QmWnVdrVQqB87RPtcqhNMv4Qdi94VTvY4bB5sxfsYRBvWK"
	}, 
"Signature": "390e9292d04d38d6a7e6225e442110fdfbe1fa2889af97288a5eb39cd9d7a97dfc62c33e7294f3560c845c194d8a239779ba5537ce4527d8bb3a36be999a8f0b26066fcf418bf67b6b25df5bd5543a0ec12b69f1cc48f0f82363c93cad550c836f92fa7d0e29d5c9b2da59da4c582b9dea131aae3085b6eaeaf77fce9ee6ed96de4bca5babb32cf8bf8b9d7568130ca30aec3d2b9d9270cb842c63244e3d5252b11194846c242492b8e145c48950441313bfb64212a92d53fd8dfcd86d508693bcc7a8b59b0ee95acc3a24bf45187550c80e8183204cc4c159b7b71ebab22500429ba879e624cca1c37051c40d964d7f64c735ab223a27c3cd7ab428bc5916334426032095772d67c5fa6f627e723ed793e674db77adb7b49587d6aa0e35b9a5d375b9533b3cffa70433467a99b460f42dc98bbfb82542bdfc572794ac451598dfe654f32f22ac59af6c8f6f0ea6f22954f5e3649f731177bdbe691e1e9ed9a03bfcf937b2c179cd6fcf0e0111226a6d28c3d4183183e7168abc022b7346c9810580469cb872c4554569268dd53a55b476a12a36f914cf4f08e8b4c67eb67c99e1a0d45d8fed9d39d1e09956192293eb1d831d85757d2f3f6a870cd7c9b79bfc5daed35f611395ad11b9e2dd1421a9d866f111676fb2df1c96599b8dbfece1ad9de715c4a2913d8ee21e0c12e8dbb299a3c3a5a7431ae7d26314d335280221cb7c290b39238f88d3b742d748a0bf74e692f7eab104f6453eaa9fa4e5e28d30ef4edda62fac43737962585a0735f4cebbf276f669d6813512f83126433b1a4b2b522e0d7a733b7e9217cccc23ddacdc0884ea3a4dfcbf456bb8a5e2c0c6db9087f6785a90f43f6d9f21d56848ce44530f9f70b4ac118d0308af64392dec2656860d81a463eadb7254c7308c298430f07fdaa5c940"}
'''

#initialize_account_users(100)


f = open("SupportFiles/address_to_account.json")
content = f.read()
f.close()
address_to_account = json.loads(content)

f = open("SupportFiles/account_to_address.json")
content = f.read()
f.close()
account_to_address = json.loads(content)


#print("********************************")

#print(address_to_account)
#print()
#print()
#print(account_to_address)

#print()
#print()

#print("******************************")
selections={}
log_entries =[]
clear_pending()
f = open("SupportFiles/addresses.txt")
addresses = f.readlines()
f.close()
total_addresses = len(addresses) -1


#initial_committee = initialize_initial_committee()
initial_committee, committee_size = initialize_initial_committee_updated()
#print("********************************")

#print(address_to_account)
#print()
#print()
#print(account_to_address)

#print()
#print()

#a = input("::::::")

print("COMMITTEE SIZE: ", committee_size)
initial_account_state = initialize_account_state()
initial_reward_state = initialize_reward_state()
members = load_committee()

f = open("SupportFiles/addresses.txt")
addresses_full = f.readlines()
f.close()

f = open("SupportFiles/accounts.txt")
accounts_full = f.readlines()

f.close()
#new_state = update_accout_state(x,members)
#print("UPDATED STATE ID: ", new_state)
set_behavior()
behaviors = load_behavior()
#a = input("PAUSE")
#should_add_count =900
#print("SHOULD ADD: ", should_add_count)

#print("INIITAL ACCOUNT STATE: ", initial_account_state)
cid, blockHeight, blockRef, validationRef, new_account_state, new_reward_state, committee_id = createMetaBlock("",0,"","",initial_account_state,initial_reward_state,initial_committee)
print("GENESIS CREATED")
for i in range (1,10000):
    cid, blockHeight, blockRef, validationRef, new_account_state, new_reward_state, committee_id  = createMetaBlock(cid, blockHeight, blockRef, validationRef, new_account_state, new_reward_state, committee_id)
print()

print("*****************************************")
print()
print(log_entries)
final_log={}
final_log["entries"] = log_entries
f = open("SupportFiles/log.json","w")
f.write(json.dumps(final_log))
f.close()

print()
print()
print(selections)
f = open("SupportFiles/selections.json","w")
f.write(json.dumps(selections))
f.close()

ipfshttphelper.close()