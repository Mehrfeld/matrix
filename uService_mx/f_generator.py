import dill as pickle





def model( model_input_a=1, model_input_b=1, model_input_c=1, model_input_d=1,
                model_input_e=1, model_input_f=1, model_input_g=1, model_input_h=1):


    model_output_a = model_input_a + model_input_b
    model_output_b = model_input_c + model_input_d
    model_output_c = model_input_e + model_input_f
    model_output_d = model_input_g + model_input_h


    return model_output_a, model_output_b, model_output_c, model_output_d
    



pickle.dump(model, open( "./models/model_0001.mdl", "wb" ) )


