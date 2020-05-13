import dill as pickle

def model_xxx(temperature=20, value_1=1, value_2=1, value_3=1):

    f = 3*temperature + value_1 + value_2 + value_3


    return f
    



pickle.dump(model_xxx, open( "./models/model_0003.mdl", "wb" ) )


