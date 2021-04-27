import pandas as pds



experiments = {"exp1": {"some key": "some value"}}



pds.DataFrame(experiments).to_csv("out.csv")

