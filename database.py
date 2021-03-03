from app import mysql,session
from Blockchain import Block,Blockchain

class table:
    def __init__(self, table_name, *args):
        self.table = table_name
        self.columns = "(%s)" %",".join(args)
        self.columnsList = args

        if isnewtable(table_name):
            create_data = "".join(
                "%s varchar(100)," % column for column in self.columnsList
            )
            cur = mysql.connection.cursor() #create the table
            cur.execute("CREATE TABLE %s(%s)" %(self.table, create_data[:len(create_data)-1]))
            cur.close()


    def getall(self):
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM %s" % self.table)
        return cur.fetchall()

    def getone(self, search, value):
        data = {}
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM %s WHERE %s = \"%s\"" % (self.table, search, value))
        if result > 0: data = cur.fetchone()
        cur.close()
        return data

    def deleteone(self, search, value):
        cur = mysql.connection.cursor()
        cur.execute("DELETE from %s where %s = \"%s\"" % (self.table, search, value))
        mysql.connection.commit()
        cur.close()

    def deleteall(self):
        self.drop()  # remove table and recreate
        self.__init__(self.table, *self.columnsList)

    def drop(self):
        cur = mysql.connection.cursor()
        cur.execute("DROP TABLE %s" % self.table)
        cur.close()

    def insert(self, *args):
        data = ""
        for arg in args:  # convert data into string mysql format
            data += "\"%s\"," % (arg)

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO %s%s VALUES(%s)" % (self.table, self.columns, data[:len(data) - 1]))
        mysql.connection.commit()
        cur.close()

def sql_raw(execution):
    cur = mysql.connection.cursor()
    cur.execute(execution)
    mysql.connection.commit()
    cur.close()

def isnewtable(name_table):
    cur = mysql.connection.cursor()

    try:
        result = cur.execute("SELECT * from %s" %name_table)
        cur.close()
    except:
        return True
    else:
        return False

def isnewuser(username):
    users = table("users", "name", "email", "username", "password")
    data = users.getall()
    print(data,"\n")
    usernames = [user.get('username') for user in data]

    return username not in usernames

def data_blockchain():
    blockchain = Blockchain()
    blockchain_table = table("blockchain", "number", "hash", "previous", "data", "nonce")
    for b in blockchain_table.getall():
        blockchain.add(Block(int(b.get('number')), b.get('previous'), b.get('data'), int(b.get('nonce'))))

    return blockchain
def update_blockchain(blockchain):
    blockchain_data = table("blockchain", "number", "hash", "previous", "data", "nonce")
    blockchain_data.deleteall()

    for block in blockchain.chain:
        blockchain_data.insert(str(block.number), block.hash(), block.previous_hash, block.data, block.nonce)

def check_chain():
    blockchain = Blockchain()
    database = ["hello", "goodbye", "test", " here"]

    num = 0

    for data in database:
        num += 1
        blockchain.mine(Block(number=num, data=data))
    update_blockchain(blockchain)
