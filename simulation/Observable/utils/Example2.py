# pyright: reportUnusedVariable=false, reportGeneralTypeIssues=false, reportUnusedImport=false
from __future__ import annotations

from Observer import Observer, Observable
import uuid

class Bank:
    def __init__(self):
        self.accounts = []
        self._sendMoneyNotifier = Bank.SendMoneyNotifier(self)
        self._transactions = []
        self._transactionId = 0
        
    def _getSendMoneyNotifier(self):
        return self._sendMoneyNotifier
    
    sendMoneyNotifier:Bank.SendMoneyNotifier = property(_getSendMoneyNotifier)
    
    def requestTransferDetails(self, fromBankAccountName:str, originatorTransactionId:str):
        return next((t for t in self._transactions if t['originatorTransactionId'] == originatorTransactionId and t['fromAccount'] == fromBankAccountName), None)
    
    def sendMoney(self, fromAccount:BankAccount, toAccount:BankAccount, amount:float, originatorTransactionId:str):
        fromAccount.balance -= amount
        toAccount.balance += amount
        self._transactionId += 1
        self._transactions.append({
            'fromAccount': fromAccount.name,
            'toAccount': toAccount.name,
            'amount': amount,
            'id': self._transactionId,
            'originatorTransactionId': originatorTransactionId
        })
        self._sendMoneyNotifier.notifyListeners(fromAccount.name, originatorTransactionId)
        
    class SendMoneyNotifier(Observable):
        def __init__(self, outer:Bank):
            super().__init__()
            self.outer:Bank = outer
            
        def notifyListeners(self, fromBankAccountName:str, originatorTransactionId:str):
            self.setChanged()
            super().notifyObservers(fromBankAccountName=fromBankAccountName, originatorTransactionId=originatorTransactionId)
            

class BankAccount:
    def __init__(self, name, balance:float, bank:Bank) -> None:
        self.name = name
        self.balance = balance
        self._bank = bank
        self._bankSendsMoneyObserver = BankAccount.BankSendsMoneyObserver(self)
        self._bank.sendMoneyNotifier.addObserver(self._bankSendsMoneyObserver)
        self._waitingTransactionsSettle = []
        
    def __eq__(self, __o: object) -> bool:
        return bool(isinstance(__o,BankAccount) and self.name == __o.name)
    
    def authoriseTransaction(self, toAccount:BankAccount, amount:float):
        id = str(uuid.uuid4())
        self._waitingTransactionsSettle.append(id)
        self._bank.sendMoney(self, toAccount, amount=amount, originatorTransactionId=id)
        
    class BankSendsMoneyObserver(Observer):
        def __init__(self,outer:BankAccount) -> None:
            super().__init__()
            self.outer = outer
        
        def update(self, observable, **kwargs):
            '''self._bank notified us that it has sent money, check if we are in the arg and then do something if we are?'''
            fromBankAccountName = kwargs['fromBankAccountName']
            originatorTransactionId = kwargs['originatorTransactionId']
            if originatorTransactionId in self.outer._waitingTransactionsSettle:
                self.outer._waitingTransactionsSettle.remove(originatorTransactionId)
                transaction = self.outer._bank.requestTransferDetails(self.outer.name, originatorTransactionId)
                
                amount:float = transaction['amount']
                accountFromName:str = transaction['fromAccount']
                accountToName:str = transaction['toAccount']
                if accountFromName == self.outer.name:
                    # Event this BankAccount sent money success
                    print(f'BankAccount_{self.outer.name} has sent {amount} to BankAccount_{accountToName}')
                elif accountToName == self.outer.name:
                    # Event this BankAccount has received Money Success
                    print(f'BankAccount_{self.outer.name} has received {amount} from BankAccount_{accountFromName}')
                
                
bank = Bank()
accountA = BankAccount('A', 100.0, bank)
accountB = BankAccount('B', 50.0, bank)

accountA.authoriseTransaction(accountB, amount=10.0)


accountB.authoriseTransaction(accountA, amount=20.0)

assert accountA.balance == 110.0
assert accountB.balance == 40.0

pass
            
        
    
    
        