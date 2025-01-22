from passlib.context import CryptContext
from sqlalchemy.orm import Session
from faker import Faker

from app.sql import models

# cuisines : 20
# entretien : 30
# accueil : 15
# docteurs : 20
# infirimières : 95
# RH : 10
# parc auto : 5
# it : 5


roles = [
    {"name": "it", "label": "Service IT"},
    {"name": "nurses", "label": "Service Infirmières"},
    {"name": "doctors", "label": "Service Médecin Chef"},
    {"name": "cleaning", "label": "Service Entretien"},
    {"name": "vehicles", "label": "Service Parc Auto"},
    {"name": "kitchen", "label": "Service Cuisines"},
    {"name": "home", "label": "Service Accueil"},
    {"name": "hr", "label": "Service RH"},
]

objects = [
    {"first_name": "ana", "last_name": "gilbert"},
    {"first_name": "katherine", "last_name": "miller"},
    {"first_name": "martin", "last_name": "lawrence"},
    {"first_name": "krystal", "last_name": "brown"},
    {"first_name": "gregory", "last_name": "hernandez"},
    {"first_name": "sandra", "last_name": "powers"},
    {"first_name": "peter", "last_name": "valdez"},
    {"first_name": "anne", "last_name": "richardson"},
    {"first_name": "elizabeth", "last_name": "baker"},
    {"first_name": "tina", "last_name": "soto"},
    {"first_name": "john", "last_name": "matthews"},
    {"first_name": "zachary", "last_name": "sims"},
    {"first_name": "shelly", "last_name": "herring"},
    {"first_name": "timothy", "last_name": "berry"},
    {"first_name": "emily", "last_name": "ramsey"},
    {"first_name": "michael", "last_name": "cohen"},
    {"first_name": "maureen", "last_name": "wallace"},
    {"first_name": "amanda", "last_name": "byrd"},
    {"first_name": "sean", "last_name": "barron"},
    {"first_name": "herbert", "last_name": "rodriguez"},
    {"first_name": "andres", "last_name": "cochran"},
    {"first_name": "mary", "last_name": "webster"},
    {"first_name": "phillip", "last_name": "andrews"},
    {"first_name": "cheryl", "last_name": "johnson"},
    {"first_name": "daniel", "last_name": "cook"},
    {"first_name": "jonathan", "last_name": "thornton"},
    {"first_name": "amy", "last_name": "taylor"},
    {"first_name": "amy", "last_name": "bryant"},
    {"first_name": "richard", "last_name": "simpson"},
    {"first_name": "samantha", "last_name": "barnes"},
    {"first_name": "andrew", "last_name": "white"},
    {"first_name": "kimberly", "last_name": "alexander"},
    {"first_name": "christian", "last_name": "everett"},
    {"first_name": "dylan", "last_name": "hayes"},
    {"first_name": "katie", "last_name": "russell"},
    {"first_name": "teresa", "last_name": "yoder"},
    {"first_name": "jaime", "last_name": "baker"},
    {"first_name": "jeremy", "last_name": "wallace"},
    {"first_name": "shannon", "last_name": "cunningham"},
    {"first_name": "elizabeth", "last_name": "henderson"},
    {"first_name": "paul", "last_name": "hutchinson"},
    {"first_name": "christopher", "last_name": "turner"},
    {"first_name": "brent", "last_name": "buchanan"},
    {"first_name": "jeremiah", "last_name": "cisneros"},
    {"first_name": "james", "last_name": "tucker"},
    {"first_name": "kenneth", "last_name": "martin"},
    {"first_name": "ricky", "last_name": "baxter"},
    {"first_name": "christopher", "last_name": "clark"},
    {"first_name": "bill", "last_name": "bender"},
    {"first_name": "miranda", "last_name": "nolan"},
    {"first_name": "brenda", "last_name": "nicholson"},
    {"first_name": "michael", "last_name": "anderson"},
    {"first_name": "amanda", "last_name": "martin"},
    {"first_name": "linda", "last_name": "johnson"},
    {"first_name": "dennis", "last_name": "rivera"},
    {"first_name": "alfred", "last_name": "wong"},
    {"first_name": "richard", "last_name": "sellers"},
    {"first_name": "erica", "last_name": "cordova"},
    {"first_name": "allison", "last_name": "colon"},
    {"first_name": "tanya", "last_name": "johnson"},
    {"first_name": "louis", "last_name": "brandt"},
    {"first_name": "ashley", "last_name": "mendez"},
    {"first_name": "ryan", "last_name": "soto"},
    {"first_name": "troy", "last_name": "grimes"},
    {"first_name": "natalie", "last_name": "copeland"},
    {"first_name": "karen", "last_name": "bridges"},
    {"first_name": "derek", "last_name": "mooney"},
    {"first_name": "sarah", "last_name": "riley"},
    {"first_name": "john", "last_name": "payne"},
    {"first_name": "sara", "last_name": "bray"},
    {"first_name": "joseph", "last_name": "hensley"},
    {"first_name": "carolyn", "last_name": "allen"},
    {"first_name": "joy", "last_name": "villarreal"},
    {"first_name": "sandy", "last_name": "wilcox"},
    {"first_name": "margaret", "last_name": "jones"},
    {"first_name": "kelli", "last_name": "webster"},
    {"first_name": "tony", "last_name": "yu"},
    {"first_name": "misty", "last_name": "carpenter"},
    {"first_name": "jay", "last_name": "roberson"},
    {"first_name": "sarah", "last_name": "turner"},
    {"first_name": "tracy", "last_name": "mullen"},
    {"first_name": "brian", "last_name": "gray"},
    {"first_name": "candace", "last_name": "park"},
    {"first_name": "pam", "last_name": "christian"},
    {"first_name": "george", "last_name": "hicks"},
    {"first_name": "samantha", "last_name": "anthony"},
    {"first_name": "troy", "last_name": "harmon"},
    {"first_name": "kristina", "last_name": "martinez"},
    {"first_name": "joshua", "last_name": "lang"},
    {"first_name": "aaron", "last_name": "montgomery"},
    {"first_name": "andrew", "last_name": "wade"},
    {"first_name": "jacob", "last_name": "jenkins"},
    {"first_name": "amy", "last_name": "freeman"},
    {"first_name": "tyler", "last_name": "ramos"},
    {"first_name": "edward", "last_name": "grant"},
    {"first_name": "samuel", "last_name": "forbes"},
    {"first_name": "michael", "last_name": "freeman"},
    {"first_name": "james", "last_name": "ford"},
    {"first_name": "stacey", "last_name": "norris"},
    {"first_name": "jason", "last_name": "schneider"},
    {"first_name": "stacey", "last_name": "wall"},
    {"first_name": "nancy", "last_name": "kelly"},
    {"first_name": "amanda", "last_name": "peterson"},
    {"first_name": "elizabeth", "last_name": "palmer"},
    {"first_name": "brandon", "last_name": "williams"},
    {"first_name": "john", "last_name": "grant"},
    {"first_name": "miranda", "last_name": "bird"},
    {"first_name": "andrea", "last_name": "kirby"},
    {"first_name": "paul", "last_name": "thomas"},
    {"first_name": "ashley", "last_name": "bryant"},
    {"first_name": "michael", "last_name": "rivera"},
    {"first_name": "morgan", "last_name": "kelley"},
    {"first_name": "hector", "last_name": "christian"},
    {"first_name": "eric", "last_name": "mora"},
    {"first_name": "paula", "last_name": "moore"},
    {"first_name": "gina", "last_name": "nicholson"},
    {"first_name": "monique", "last_name": "tate"},
    {"first_name": "monica", "last_name": "gallagher"},
    {"first_name": "autumn", "last_name": "robinson"},
    {"first_name": "theresa", "last_name": "barton"},
    {"first_name": "amy", "last_name": "vargas"},
    {"first_name": "april", "last_name": "stanley"},
    {"first_name": "karen", "last_name": "berger"},
    {"first_name": "richard", "last_name": "flores"},
    {"first_name": "spencer", "last_name": "sandoval"},
    {"first_name": "angel", "last_name": "lopez"},
    {"first_name": "patricia", "last_name": "kaiser"},
    {"first_name": "alexander", "last_name": "klein"},
    {"first_name": "andrew", "last_name": "massey"},
    {"first_name": "brianna", "last_name": "petty"},
    {"first_name": "tiffany", "last_name": "george"},
    {"first_name": "stephanie", "last_name": "foster"},
    {"first_name": "william", "last_name": "shaw"},
    {"first_name": "dorothy", "last_name": "lambert"},
    {"first_name": "daniel", "last_name": "scott"},
    {"first_name": "joshua", "last_name": "patterson"},
    {"first_name": "ray", "last_name": "wilson"},
    {"first_name": "katrina", "last_name": "hoffman"},
    {"first_name": "raven", "last_name": "holmes"},
    {"first_name": "amy", "last_name": "miles"},
    {"first_name": "douglas", "last_name": "dudley"},
    {"first_name": "brandi", "last_name": "wilson"},
    {"first_name": "lisa", "last_name": "reid"},
    {"first_name": "kirk", "last_name": "lewis"},
    {"first_name": "michael", "last_name": "irwin"},
    {"first_name": "rachel", "last_name": "solomon"},
    {"first_name": "douglas", "last_name": "cooper"},
    {"first_name": "melanie", "last_name": "hicks"},
    {"first_name": "megan", "last_name": "frank"},
    {"first_name": "christina", "last_name": "patton"},
    {"first_name": "destiny", "last_name": "williams"},
    {"first_name": "anthony", "last_name": "cox"},
    {"first_name": "heather", "last_name": "peterson"},
    {"first_name": "russell", "last_name": "bell"},
    {"first_name": "anthony", "last_name": "weiss"},
    {"first_name": "kimberly", "last_name": "horton"},
    {"first_name": "kathleen", "last_name": "schaefer"},
    {"first_name": "sarah", "last_name": "pierce"},
    {"first_name": "richard", "last_name": "miller"},
    {"first_name": "danielle", "last_name": "roberson"},
    {"first_name": "jessica", "last_name": "rose"},
    {"first_name": "david", "last_name": "potts"},
    {"first_name": "andrew", "last_name": "buchanan"},
    {"first_name": "jeffrey", "last_name": "hall"},
    {"first_name": "daniel", "last_name": "smith"},
    {"first_name": "corey", "last_name": "velez"},
    {"first_name": "catherine", "last_name": "lowe"},
    {"first_name": "aaron", "last_name": "smith"},
    {"first_name": "micheal", "last_name": "doyle"},
    {"first_name": "robert", "last_name": "love"},
    {"first_name": "jennifer", "last_name": "wallace"},
    {"first_name": "kimberly", "last_name": "flores"},
    {"first_name": "gary", "last_name": "caldwell"},
    {"first_name": "theresa", "last_name": "golden"},
    {"first_name": "lynn", "last_name": "daniels"},
    {"first_name": "michael", "last_name": "parker"},
    {"first_name": "amanda", "last_name": "nguyen"},
    {"first_name": "thomas", "last_name": "marshall"},
    {"first_name": "robert", "last_name": "johnson"},
    {"first_name": "jacob", "last_name": "lutz"},
    {"first_name": "hannah", "last_name": "brewer"},
    {"first_name": "alexander", "last_name": "jackson"},
    {"first_name": "tracy", "last_name": "robinson"},
    {"first_name": "wendy", "last_name": "daniels"},
    {"first_name": "kristi", "last_name": "boyd"},
    {"first_name": "ralph", "last_name": "avila"},
    {"first_name": "heather", "last_name": "booker"},
    {"first_name": "shane", "last_name": "edwards"},
    {"first_name": "dana", "last_name": "ruiz"},
    {"first_name": "elizabeth", "last_name": "davis"},
    {"first_name": "patrick", "last_name": "white"},
    {"first_name": "christopher", "last_name": "mccarthy"},
    {"first_name": "angela", "last_name": "jones"},
    {"first_name": "cynthia", "last_name": "moore"},
    {"first_name": "kevin", "last_name": "morris"},
    {"first_name": "edwin", "last_name": "schwartz"},
    {"first_name": "james", "last_name": "fisher"},
    {"first_name": "victor", "last_name": "tucker"},
    {"first_name": "marc", "last_name": "hunter"},
]

usernames: list[str] = []
for object in objects:
    username = object["first_name"] + "." + object["last_name"] + "@cmv.fr"
    usernames.append(username)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed_password = pwd_context.hash("Abcdef@123456")


# création des utilisateurs
def create_fixtures(db: Session):
    index = 0

    db_roles: list[models.Role] = []
    for elem in roles:
        role = models.Role(
            name=elem["name"],
            label=elem["label"],
        )
        db_roles.append(role)
    db.add_all(db_roles)
    db.commit()

    admin_role = db.query(models.Role).filter(models.Role.name == "it").first()
    nurse_role = db.query(models.Role).filter(models.Role.name == "nurses").first()
    home_role = db.query(models.Role).filter(models.Role.name == "home").first()

    permissions = [
        {"role": nurse_role, "action": "get", "resource": "chambres"},
        {"role": nurse_role, "action": "get", "resource": "services"},
        {"role": home_role, "action": "get", "resource": "patients"},
        {"role": home_role, "action": "get", "resource": "documents"},
        {"role": home_role, "action": "post", "resource": "documents"},
        {"role": home_role, "action": "delete", "resource": "documents"},
        {"role": home_role, "action": "post", "resource": "patients"},
        {"role": home_role, "action": "put", "resource": "patients"},
        {"role": home_role, "action": "delete", "resource": "patients"},
    ]

    db_perms: models.Permission = []
    for perm in permissions:
        db_perm = models.Permission(
            role=perm["role"],
            action=perm["action"],
            resource=perm["resource"],
        )
        db_perms.append(db_perm)

    db.add_all(db_perms)
    db.commit()

    user = models.User(
        username="admin@cmv.fr",
        password=hashed_password,
        prenom="jacques",
        nom="durand",
        is_active=True,
        service="it",
    )

    home = models.User(
        username="accueil@cmv.fr",
        password=hashed_password,
        prenom="jacqueline",
        nom="dupond",
        is_active=True,
        service="patients",
    )

    user.role = admin_role
    home.role = home_role
    home.role
    db.add(user)
    db.add(home)
    db.commit()

    users_type = [
        {"role": "it", "qty": 4},
        {"role": "vehicles", "qty": 5},
        {"role": "hr", "qty": 10},
        {"role": "kitchen", "qty": 20},
        {"role": "cleaning", "qty": 30},
        {"role": "doctors", "qty": 20},
        {"role": "nurses", "qty": 95},
        {"role": "home", "qty": 15},
    ]

    for item in users_type:
        role = db.query(models.Role).filter(models.Role.name == item["role"]).first()
        index = create_users(db, index, item["qty"], role)

    return {"message": "done"}


def create_users(db, idx, qty, role):
    db_users: list[models.User] = []
    for i in range(0, qty):
        user = models.User(
            username=usernames[idx],
            password=hashed_password,
            prenom=objects[idx]["first_name"],
            nom=objects[idx]["last_name"],
            service=role.name,
        )
        user.role = role
        db_users.append(user)
        idx += 1
    db.add_all(db_users)
    db.commit()
    return idx


def create_object():
    fake = Faker()
    object = {
        "first_name": fake.first_name().lower(),
        "last_name": fake.last_name().lower(),
    }
    return object


""" 
    for role in db_roles:
        print(f"role : {role}")
        perm_refresh = models.Permission(
            role=role.name, action="get", resource="/api/auth/refresh"
        )
        perm_user = models.Permission(
            role=role.name, action="get", resource="/api/users/me"
        )
        db_perms.append(perm_refresh)
        db_perms.append(perm_user)
 """
