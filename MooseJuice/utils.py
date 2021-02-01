from MooseJuice.models import User, Post, Prices, Goals
import pandas as pd
import numpy as np
from MooseJuice import db

def getPrices():
    if Prices.query.all():
        beer_price = Prices.query.all()[-1].beer_price
        soda_price = Prices.query.all()[-1].soda_price
    else:
        beer_price, soda_price = 5, 5
    
    return beer_price, soda_price
def getNumber(string):
    try:
        return eval(string)
    except:
        return 0

def getQuery(user):
    try:
        user_post = user.posts[-1]
    except:
        user_post = None
    return user_post

def NewPost( form, id):
    beer_price, soda_price = getPrices()
    beers, sodas = None, None
    user = User.query.filter_by(id=id).first()
    user_post = getQuery(user)
    


    if form.formType == 'Purchase':
        beers = getNumber(form.amount_beer.data)
        sodas = getNumber(form.amount_soda.data)
        amount = beers * beer_price + sodas * soda_price
        user_balance = user_post.user_balance - amount if user_post else - amount
        moose_balance = Post.query.all()[-1].moose_balance

        if (beers and beers != 0) and (sodas and sodas != 0):
            message = f"You bought {beers} {'beers' if beers > 1 else 'beer'} and {sodas} {'sodas' if sodas > 1 else 'soda'}!"

        elif (beers and beers !=0):
            message = f"You bought {beers} {'beers' if beers > 1 else 'beer'}!"

        elif (sodas and sodas !=0):
            message = f"You bought {sodas} {'sodas' if sodas > 1 else 'soda'}!"

    elif form.formType == 'Transfer':
        amount = form.transfer.data
        user_balance = user_post.user_balance + amount if user_post else + amount

        if user_balance > 1000:
            return False, "You cannot have more than 1000 kr in your Moose Account"
        moose_balance = Post.query.all()[-1].moose_balance + amount
        message = "Your account balance has been updated!"


    

    return Post(post_type = form.formType, amount = amount, beers = beers, sodas = sodas,
                user_balance = user_balance, moose_balance = moose_balance, user_id = id), message


def getRoom(user):
    return f"Room {user.room}" if "Guest" not in user.room else f"Guest {user.room.split('t')[-1]}"

def getUserbalance(user):
    user = User.query.filter_by(id=user.id).first()
    latest_post = getQuery(user)
    if latest_post:
        category = ("danger" if latest_post.user_balance < 0 else "success") if user.status != 'admin' else ("danger" if Post.query.all()[-1].moose_balance < 0 else "success")
        user_balance = latest_post.user_balance if user.status != 'admin' else Post.query.all()[-1].moose_balance
    else:
        category = "success"
        user_balance = 0

    return category, user_balance


class activeTab:
    balance = ["active","show active"]
    post    = ["", ""]
    update  = ["", ""]
    date    = ["active", "show active"]
    week    = ["", ""]
    month    = ["", ""]

    active  = ["active", "show active"]
    inactive  = ["", ""]

    def updateTab(self, method):
        if method == "balance":
            self.balance = self.active
            self.update = self.inactive
            self.post  = self.inactive
        elif method == "update":
            self.balance = self.inactive
            self.update = self.active
            self.post  = self.inactive
        elif method == "post":
            self.post  = self.active
            self.balance = self.inactive
            self.update = self.inactive
        elif method == "date":
            self.date  = self.active
            self.week = self.inactive
            self.month = self.inactive
        elif method == "week":
            self.date  = self.inactive
            self.week = self.active
            self.month = self.inactive
        elif method == "month":
            self.date  = self.inactive
            self.week = self.inactive
            self.month = self.active

Tab = activeTab()


def getDF(user):
    Posts_order_asc = Post.query.filter_by(user_id = user.id).all()
    postHeadings = ["Date", "Week", "Month", "Type", "Beers", "Sodas", "Amount", "Balance"]
    if Posts_order_asc:
        PostsTable = [(p.date.strftime('%d-%m-%Y'), p.date.strftime("%V (%Y)"), p.date.strftime("%B (%Y)"),
        p.post_type, p.beers, p.sodas, p.amount, p.user_balance) for p in Posts_order_asc]

    else:
        PostsTable = [tuple(["" for _ in postHeadings]) for i in range(3)]

    df = pd.DataFrame(PostsTable, columns = postHeadings)
    return df
    
def groupBy(df, what):
    df_transfer = df[df["Type"] == 'Transfer'].groupby([what]).sum()
    df_purchase = df[df["Type"] == 'Purchase'].groupby([what]).sum()
    df_balance  = df.groupby([what]).last()

    df_purchase["Transfer"] = df_transfer["Amount"]
    df_purchase["Balance"]  = df_balance["Balance"]

    postHeadings = [what, "Beers", "Sodas", "Total Price", "Transfer", "End of the day Balance"]
    df = df_purchase.reset_index()[[what, "Beers","Sodas", "Amount", "Transfer", "Balance"]].fillna("0").applymap(str)

    

    return df.iloc[::-1]


def getDFPost():
    post = Post.query.all()
    postHeadings = ["Date", "Username", "Status", "Type", "Amount", "Beers", "Sodas", "User Balance", "Moose Balance"]

    post = [(p.date.strftime('%d-%m-%Y'), p.author.username, p.author.status, p.post_type, p.amount, p.beers, p.sodas, p.user_balance, p.moose_balance) for p in post]
    df = pd.DataFrame(post, columns = postHeadings)

    return df

class MooseStats:
    def __init__(self, df):

        post = Post.query.all()
        self.active = df[df["Status"] == 'active']
        self.admin  = df[df["Status"] == 'admin']
        self.active_grouped = self.active.groupby(["Username"]).agg({'Beers': 'sum', 'Sodas': 'sum', 'User Balance': 'last'}).reset_index()
        self.in_da_bank =  int(np.ceil(float(post[-1].moose_balance)))
        self.no_outstanding = int(np.ceil(float(self.in_da_bank - self.active_grouped["User Balance"].sum())))

        self.category1 = "danger" if self.in_da_bank < 0 else "info"
        self.category2 = "danger" if self.no_outstanding < 0 else "info"
        self.beer_score = [(i + 1 , U[0], U[1]) for i, U in enumerate(self.active_grouped.sort_values(["Beers"], ascending = False)[["Beers", "Username"]].values)]
        self.soda_score = [(U[0], U[1]) for U in self.active_grouped.sort_values(["Sodas"], ascending = False)[["Sodas", "Username"]].values]

        self.score_table = [self.beer_score[i] + (" ",) + self.soda_score[i] for i in range(len(self.beer_score))]

def updateProgress():
    mb = MooseStats(getDFPost()).no_outstanding
    goals = Goals.query.all()
    

    for goal in goals:
        
        goal.progress = max(0,  min(100,  (mb-1000)/goal.price *100 ))
        
    
    db.session.commit()
def updatePosts(stats = False):
    
    post_table = getDFPost()
    admin_post = post_table[post_table["Status"] == 'admin'][1:]
    other_post = post_table[post_table["Status"] != 'admin']

    posts = Post.query.all()
    edits = list(filter(None, [(i, P) if (P.comment != None and "CHECKED" not in P.comment) else None for i,P in enumerate(posts)]))
    if not stats:
        for i, p in edits:
            if p.author.status != 'admin':
                latest = list(filter(None, [user_p if user_p.date < p.date else None for user_p in p.author.posts]))[-1]
                if p.post_type == 'Transfer':
                    p.user_balance = latest.user_balance + p.amount
                    p.moose_balance = posts[i-1].moose_balance + p.amount
                else:
                    p.user_balance = latest.user_balance  - p.amount
                    p.moose_balance = posts[i-1].moose_balance
            else:
                if p.post_type == 'Transfer':
                    p.moose_balance = posts[i-1].moose_balance + p.amount
                else:
                    p.moose_balance = posts[i-1].moose_balance - p.amount

            p.comment += " CHECKED"

        db.session.commit()

    else:  
        beers = admin_post[["Beers", "Sodas"]].sum()["Beers"] - other_post[["Beers", "Sodas"]].sum()["Beers"]
        sodas = admin_post[["Beers", "Sodas"]].sum()["Sodas"] - other_post[["Beers", "Sodas"]].sum()["Sodas"]

        return int(beers), int(sodas)