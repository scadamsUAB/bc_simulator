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
def set_behavior(amount1, amount2):
    f = open("SupportFiles/addresses.txt")
    addresses = f.readlines()
    f.close()
    count =0

    account_behavior={}
    for a in addresses:
        if count < amount1:
            account_behavior[str(a.strip())]=0
            count = count +1
        elif count>=amount1 and count<amount2:
            account_behavior[str(a.strip())]=1
        else:
            account_behavior[str(a.strip())]=2
    f = open("SupportFiles/behavior.json","w")
    f.write(json.dumps(account_behavior))
    f.close()    

#### TESTING ONLY
def load_behavior():
    f = open("SupportFiles/behavior.json")
    behaviors = f.read()
    f.close()
    behaviors = json.loads(behaviors)
   # print(behaviors)
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
   # print("INITIALIZE ACCOUNT STATE",y)
    f = open("SupportFiles/temp.txt","w")
    f.write(y)
    f.close()
    return(ipfshttphelper.getCID("SupportFiles/temp.txt"))

#### TESTING ONLY??
def initialize_reward_state():
    x = {}
    y = json.dumps(x)
  #  print("INITIALIZE REWARD STATE",y)
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
    
    f = open("SupportFiles/address_to_account.json","w")
    f.write(json.dumps(address_to_account))
    f.close()

    f = open("SupportFiles/account_to_address.json","w")
    f.write(json.dumps(account_to_address))
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
        print("USER ADDRESS   ", user_address, i)
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
    if i in range(0,10):
        print(pending[i])
 #   cleaned_pending =[]
    print("PENDING SIZE",len(pending))
    selected = []
    random.shuffle(pending)
    while len(selected) < committee_size:
        index = random.randint(0,len(pending)-1)
        if index in selected:
            print("ALREADY SELECTED")
        else:
            addr = get_text_content_from_ipfs(pending[index])
            addr = json.loads(addr)
            addr = addr["address"]
            score = 0
            if addr in reward_state:
                score = reward_state[addr.replace("\n","")]
            else:
                score = 0
            should_add = should_add_member(modifier, score)
            if should_add:
                selected.append(index)
    print("SELECTED INDEXES: ", selected)
    new_users = []

    for user in selected:
        usercid = pending[user]
       
        usercid = usercid.replace("\n","")
        content = get_text_content_from_ipfs(usercid)
        content = json.loads(content)
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



def bootstrap_select(modifier, reward_state_CID, bootstrap_list):
    print("BOOTSTRAP SELECTION")
    reward_state = get_text_content_from_ipfs(reward_state_CID)
    reward_state = json.loads(reward_state)
  
    f = open("SupportFiles/pending.txt")
    pending = f.readlines()
    f.close()
    if i in range(0,10):
        print(pending[i])
    selected = []
    random.shuffle(pending)
    while len(selected) < committee_size/2:
        index = random.randint(0,len(pending)-1)
        if index in selected:
            print("ALREADY SELECTED")
        else:
            addr = get_text_content_from_ipfs(pending[index])
            addr = json.loads(addr)
            addr = addr["address"]
            score = 0
            if addr in reward_state:
                score = reward_state[addr.replace("\n","")]
            else:
                score = 0
            should_add = should_add_member(modifier, score)
            if should_add:
                selected.append(index)
    print("SELECTED INDEXES: ", selected)
    new_users = []

    for user in selected:
        usercid = pending[user]
       
        usercid = usercid.replace("\n","")
        content = get_text_content_from_ipfs(usercid)
        content = json.loads(content)
        new_users.append(content)
   
    f = open("SupportFiles/currentCommittee.txt","w")
    f.close()
    new_addresses = []
   
    remaining_members = committee_size- int((committee_size/2))
    selected_bootstrap = []
    total_selected = len(selected)
    while total_selected < committee_size:
        
        index = random.randint(0,len(bootstrap_list)-1)
        if  index in selected:
            pass
        elif index in selected_bootstrap:
            pass
        else:
            usercid = bootstrap_list[index]
        
            usercid = usercid.replace("\n","")
            content = get_text_content_from_ipfs(usercid)
            content = json.loads(content)
            if content in new_users:
                pass
            else:
                new_users.append(content)
                total_selected = total_selected + 1
    for nu in new_users:
        new_addresses.append(nu["address"].strip())
    f = open("SupportFiles/currentCommittee.txt","a")
    for na in new_addresses:
        f.write(na+"\n")
    f.close()
   
    members ={}
    members["members"] = new_users
    f = open("SupportFiles/temp.txt","w")
    f.write(json.dumps(members))
    f.close()
    new_committee_CID = ipfshttphelper.addFileByPath("SupportFiles/temp.txt")
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
    print("REWARD STATE")
    print(reward_state)
   
   # for x in reward_state:
   #     print(len(x))
    for m in members:
   #     print("CHECKING", m,len(m),reward_state[m+"\n"])
        if len(m) == 46:
            print(m)
            if account_to_address[m] in reward_state:
               # print("appending value from reward")
               # print(m)
               # a = input("PAUSE")
                scores.append(reward_state[account_to_address[m]])
            else:
                scores.append(0)
    print(scores)
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

def update_account_state(account_state, members, honest_array, block_proposer_index, honest_count, malicious_count, lazy_count, block_height):
    account_state_content = ipfshttphelper.getContent(account_state,"NA")
    try:
        account_state_content = account_state_content.decode('UTF-8')
    except:
        pass
    
    try:
        account_state_object = json.loads(account_state_content)
    except:
        print("ERROR PARSING ACCOUNT STATE")
        account_state_object = account_state_content
   # print(honest_array, block_proposer_index)
    if honest_array[block_proposer_index] == 0 or honest_array[block_proposer_index] == 2: ### HONEST OR LAZY PROPOSER
        
        if honest_count + lazy_count > malicious_count:  ### REWARD HONEST AND LAZY NODES
            for i in range(0, len(members)):
           
                if honest_array[i] == 0 or honest_array[i]==2:
                    account_state_object = reward_member(account_state_object,members[i].replace("\n",""))
                else:
                    account_state_object =  penalize_member(account_state_object,members[i].replace("\n",""))
        else:
            for i in range(0, len(members)):
               
                if honest_array[i] == 0 or honest_array[i]==2:
                    account_state_object = penalize_member(account_state_object,members[i].replace("\n",""))
                else:
                    account_state_object =  reward_member(account_state_object,members[i].replace("\n",""))
    else: ## MALCIOUS LEADER
        if malicious_count + lazy_count > honest_count:  ### REWARD MALICIOUS AND LAZY NODES *** NEED TO LOG
            for i in range(0, len(members)):
                if honest_array[i] == 1 or honest_array[i]==2:
                    account_state_object = reward_member(account_state_object,members[i].replace("\n",""))
                else:
                    account_state_object =  penalize_member(account_state_object,members[i].replace("\n",""))

            f = open("SupportFiles/__maliciousblocks_log.txt", "a")
            f.write(str(block_height)+","+str(honest_count)+","+str(malicious_count)+","+str(lazy_count)+"\n")
            f.close()


        else: ### MALICIOUS LEADER BUT MORE HONEST THAN LAZY + MALICIOUS
            for i in range(0, len(members)):
                if honest_array[i] == 1 or honest_array[i]==2:
                    account_state_object = penalize_member(account_state_object,members[i].replace("\n",""))
                else:
                    account_state_object =  reward_member(account_state_object,members[i].replace("\n",""))
    
    
    account_state_content = json.dumps(account_state_object)
    f = open("SupportFiles/temp.txt","w")
    f.write(account_state_content)
    f.close()
    return ipfshttphelper.addFileByPath("SupportFiles/temp.txt")


def update_reward_state(reward_state, members, honest_array, block_proposer_index, honest_count, malicious_count, lazy_count, block_height):
    reward_state_content = ipfshttphelper.getContent(reward_state,"NA")
    try:
        reward_state_content = reward_state_content.decode('UTF-8')
    except:
        pass
    
    try:
        reward_state_object = json.loads(reward_state_content)
    except:
        reward_state_object = reward_state_content
        print("ERROR PARSING REWARD STATE")
  
  #############################3
    print(honest_array, block_proposer_index)
    if honest_array[block_proposer_index] == 0 or honest_array[block_proposer_index] == 2: ### HONEST OR LAZY PROPOSER
        
        if honest_count + lazy_count > malicious_count:  ### REWARD HONEST AND LAZY NODES
            for i in range(0, len(members)):
           
                if honest_array[i] == 0 or honest_array[i]==2:
                    reward_state_object = reward_member(reward_state_object,members[i].replace("\n",""))
                else:
                    reward_state_object =  penalize_member(reward_state_object,members[i].replace("\n",""))
        else:
            for i in range(0, len(members)):
               
                if honest_array[i] == 0 or honest_array[i]==2:
                    reward_state_object = penalize_member(reward_state_object,members[i].replace("\n",""))
                else:
                    reward_state_object =  reward_member(reward_state_object,members[i].replace("\n",""))
    else: ## MALCIOUS LEADER
        if malicious_count + lazy_count > honest_count:  ### REWARD MALICIOUS AND LAZY NODES *** NEED TO LOG
            for i in range(0, len(members)):
                if honest_array[i] == 1 or honest_array[i]==2:
                    reward_state_object = reward_member(reward_state_object,members[i].replace("\n",""))
                else:
                    reward_state_object =  penalize_member(reward_state_object,members[i].replace("\n",""))

         #   f = open("SupportingFiles/__maliciousblocks_log.txt", "a")
         #   f.write(str(block_height)+","+str(honest_count)+","+str(malicious_count)+","+str(lazy_count)+"\n")
         #   f.close()


        else: ### MALICIOUS LEADER BUT MORE HONEST THAN LAZY + MALICIOUS
            for i in range(0, len(members)):
                if honest_array[i] == 1 or honest_array[i]==2:
                    reward_state_object = penalize_member(reward_state_object,members[i].replace("\n",""))
                else:
                    reward_state_object =  reward_member(reward_state_object,members[i].replace("\n",""))
    
    
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
    f = open("SupportFiles/currentCommittee.txt")
    current_committee = f.readlines()
    f.close()
    cleaned_current_committee =[]
    for cc in current_committee:
        print("REMOVING ", cc, len(cc))
        pending.remove(str(address_to_account[cc.strip()])+"\n")
    print("Start Writing pending")

    with open("SupportFiles/pending.txt","w") as f:
        f.write("".join(pending))
    print("DONE WRITING PENDING")


def createMetaBlock(previous_meta_id, previous_meta_height, previous_block_id, previous_val_id,  account_state, reward_state, committee_id, members, honest_count, malicious_count, lazy_count, behaviors_array, block_height, block_proposer,bootstrap_list):
    should_update_log = False
    new_block = {}
    block_data = {}
    random.seed(str(previous_meta_id).strip())
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

   # print("CALCULATING ACCOUNT STATE")
    block_proposer_index = block_height %10
    new_account_state = update_account_state(account_state,members,behaviors_array,block_proposer_index,honest_count, malicious_count, lazy_count,block_height)
   # print("CALCULATING REWARD STATE")
    new_reward_state = update_reward_state(reward_state,members,behaviors_array,block_proposer_index,honest_count, malicious_count, lazy_count,block_height)

    block_data["AccountState"] = new_account_state
    block_data["RewardState"] = new_reward_state
    if(block_height +1)%10 == 2:
    
        print("ADDING PENDING MEMBER")
        add_pending_member()
    pending_id = ipfshttphelper.addFileByPath("SupportFiles/pending.txt")
    block_data["PendingMembers"] = pending_id


    print("CURRENT BLOCK HEIGHT ", block_height)
    if (block_height + 1 )% 10 == 0:
        ## NEW COMMITTEE
        print()
        print()
        print("NEW COMMITTEE SELECTION")
        pending_id = block_data["PendingMembers"]
        modifier = get_average_score_modifier(pending_id, new_reward_state)
        if epoch_id < 150:  ## Bootstrap mode
            new_committee_CID = bootstrap_select(modifier,new_reward_state,bootstrap_list)
        else:
                    
        

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
#initialize_account_users(1000)


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

print(len(account_to_address))
#initial_committee = initialize_initial_committee()
initial_committee, committee_size = initialize_initial_committee_updated()
print(len(account_to_address))
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

f = open("SupportFiles/__honest_epoch_tracker.txt","w")
f.close()

f = open("SupportFiles/__malicious_epoch_tracker.txt","w")
f.close()

f = open("SupportFiles/__maliciousblocks_log.txt","w")
f.close()



set_behavior(300,600)
behaviors = load_behavior()
honest_count = committee_size
malicious_count =0
lazy_count = 0
epoch_id =0
behaviors_array = []
members = load_committee()    
for m in members:
    mem = m.strip()
    behaviors_array.append(behaviors[mem])
index = 0
blockHeight =0
block_proposer = members[0].strip()
bootstrap_list = accounts_full[0:100]

cid, blockHeight, blockRef, validationRef, new_account_state, new_reward_state, committee_id = createMetaBlock("",0,"","",initial_account_state,initial_reward_state,initial_committee, members, honest_count, malicious_count, lazy_count,behaviors_array, blockHeight, block_proposer, bootstrap_list)
print("GENESIS CREATED")
previous_committee_id = committee_id
committee_detail = get_text_content_from_ipfs(committee_id)
committee_detail = json.loads(committee_detail)
index = blockHeight %10



for i in range (1,5000):
    index = blockHeight %10

    random.seed(cid)
    #print("Checking Members")
    block_proposer = members[index].strip()
#    print("DONE CHECKING MEMBER BEHAVIOR")    

    cid, blockHeight, blockRef, validationRef, new_account_state, new_reward_state, committee_id  = createMetaBlock(cid, blockHeight, blockRef, validationRef, new_account_state, new_reward_state, committee_id, members, honest_count, malicious_count,lazy_count,behaviors_array, blockHeight, block_proposer, bootstrap_list)
    ### IF NEW COMMITTEE RECALCULATE VALUES
    if previous_committee_id != committee_id:
        print("CHANGING COMMITTEE VALUES")
        honest_count = 0
        malicious_count =0
        lazy_count =0
        epoch_id = epoch_id + 1
        previous_committee_id = committee_id
        committee_detail = get_text_content_from_ipfs(committee_id)
        committee_detail = json.loads(committee_detail)

        behaviors_array = []
        members = load_committee()    
        for m in members:
            mem = m.strip()
            behaviors_array.append(behaviors[mem])
        
        for i in range(0,len(members)):
            if behaviors_array[i] ==0:
                honest_count = honest_count + 1
            if behaviors_array[i] ==1:
                malicious_count = malicious_count + 1
            else:
                lazy_count = lazy_count + 1
        print(members,honest_count, malicious_count, lazy_count)
        if malicious_count > honest_count:
            f = open("SupportFiles/__malicious_epoch_tracker.txt","a")
            f.write(str(epoch_id)+ ","+str(honest_count)+","+str(malicious_count)+","+str(lazy_count)+"\n")
            f.close()
        else:
            f = open("SupportFiles/__honest_epoch_tracker.txt","a")
            f.write(str(epoch_id)+ ","+str(honest_count)+","+str(malicious_count)+","+str(lazy_count)+"\n")
            f.close()
        print("*****************************************")
        print()
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
