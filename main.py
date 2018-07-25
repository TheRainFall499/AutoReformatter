import makeMapping, headerText, footerLogic

#Start the main method so-to-speak
print("Hello World!")

#clear output file
open("output.txt","w+").close()

headerText.FunctionStarts()

#input for the layout of client fields
  #need to ask if the fields have a definite length or not. 
isFixedLength = raw_input("Is the client file fixed length? Y/N")
while True:
  if(isFixedLength.upper() == "Y"):
    #input the logic for fixed length files - still use client_field_names in the end
    client_field_names_input = raw_input("Input client field names in a space delimited list. Indicate the length of the string after a \"-\" e.g. Carrier_ID-20\n")
    client_field_names = client_field_names_input.split(" ")
    break
  if(isFixedLength.upper() == "N"):
    client_field_names_input = raw_input("Input client field names in a space delimited list\n")
    client_field_names = client_field_names_input.split(" ")
    break

#call to produce header
headerText.HeaderPart(client_field_names, isFixedLength)

#starting the footer logic with the footer layout
  #input the footer_record layout fields, loop through input to put them on their own line
#while loop to contain those who don't put in a Record_Count
#some files don't have footers need to fix that one

#put an input to account for footer existing, if it does, just move on with the flag set to N
while True:
  doesFooterExist = raw_input("Does the spec indicate there is a trailer/footer? Y/N")
  if(doesFooterExist.upper() == "Y"):
    footerLogic.MakeFooterLogic()
    break
  if(doesFooterExist.upper() == "N"):
    break

#add header for mapping projection
#e.g. outputDS := project (inputNoFooter, transform(Layouts.layout_scrub_eligibility_input,
#this follows Layouts.layout_scrub_[datamodel]_input
outfile = open("output.txt", "a+")
outfile.write("\n")
model_name = raw_input("Input the data model name (e.g. eligibility, Rx_claims)\n")
if(doesFooterExist.upper() == "Y"):
  outfile.write("outputDS := project(inputNoFooter, transform(Layouts.layout_scrub_{}_input,\n".format(model_name))
else:
  outfile.write("outputDS := project(inputDS, transform(Layouts.layout_scrub_{}_input,\n".format(model_name))
outfile.close()

#input loop for invalid input - Mapping/LookUp Section
while True:
  #Input data_model_name
  #model_name = raw_input("Input the data model name (e.g. eligibility, Rx_claims)\n")
  #print(model_name)
  #Input LN field names in a space delimited list of single quoted strings
  #e.g. 1 2 3
  #client_field_names_input = raw_input("Input client field names in a space delimited list\n")
  #print(client_field_names_input)
  #Input LN field names in a space delimited list of single quoted strings
  #e.g. 1 2 3
  lexis_field_names_input = raw_input(
      "Input LN field names in a space delimited list. If the field needs mapping, add \"-Map\" to it E.G 3-Map\n")
  #print(lexis_field_names_input)

  #because on this online converter takes in input as a LIST of input...
  #convert comma delimited string into a List using the handy dandy str.split method
  #reeeeaaaallllyyy riding on the user's ability to make a properly formatted list here, btw
  #could make it space delimited too, might be easier.
  #client_field_names = client_field_names_input.split(" ")
  lexis_field_names = lexis_field_names_input.split(" ")
  #print("Debug - client_field_names: ")
  #print(client_field_names)
  #print("Debug - ln_field_names: ")
  #print(lexis_field_names)

  if (len(client_field_names) != len(lexis_field_names)):
      print("Well that's a problem. These sets are not great. Try Again")
      print("FYI here's the number of fields we saw for the client list: "+len(client_field_names))
      print("FYI here's the number of fields we saw for the LN list: "+len(lexis_field_names))
  else:
      print("Good for scripting")

      #adding in extra lines outside of mapping
      #Batch_Type for just the eligibility data model, and CustomerID and Record_Type for every data model
      outfile = open("output.txt", "a+")
      #detecting and actions for eligibility Batch_Type
      if(model_name == "eligibility"):
        #input loop for invalid input
        while True:
          print("Eligibility data model is in use. Choose a Batch_Type:")
          print("1 Refresh")
          print("2 Updates")
          print("3 Delete")
          inputBatch_Type = raw_input("Input the number corresponding to the choice. (Type a 1 2 or 3)")
          if(inputBatch_Type == "1"):
            outfile.write("self.scrub_prefix.BatchType := c.c_BatchType_Full_Refresh;\n")
            break
          if(inputBatch_Type == "2"):
            outfile.write("self.scrub_prefix.BatchType := c.c_BatchType_Delta_Updates;\n")
            break
          if(inputBatch_Type == "3"):
            outfile.write("self.scrub_prefix.BatchType := c.c_BatchType_Delete;\n")
            break
          else:
            print("Invalid Input. Try again.")

      #input for CustomerID 
      inputCustID = raw_input("Input the Constant corresponding to the CustomerID e.g. c.c_CustomerID_SC_CareFirst");
      outfile.write("self.{}.CustomerID := {};\n".format(model_name, inputCustID))

      #Record_Type is hardcoded
      outfile.write("self.{}.Record_Type := c.c_Record_Type_Detail;\n".format(model_name))
      outfile.close()

      #loop through the zipped client vs LN fields, asking if additional mapping is needed for each pairing
      #so there's a thought. If I continuously ask like this... it's not immediately copy-and-paste-able
      #you'd have to get rid of the "Does ___ require additional mapping" lines, THEN it would be good
      #so it's either do that... or take out user input, and just have them put in a flag for mapping on the client fields
      #it'll be a bit more work on the user's end, to be sure, to maybe add a "M-" at the beginning of the mapped fields
      #then on my end, it's just if there's an "M-" slice it off, then pass it through the MakeMapping, if not, pass through
      #the format from MakeSkeleton
      #for now I'll just do a simple implementation of Y/N

      for ln_field, client_field in zip(lexis_field_names, client_field_names):
        if("-" in client_field):
          client_field = client_field[:client_field.find("-")]
        if("Date" in ln_field):
          print(ln_field+" is a apparently date field and may need to be parsed.")

          dateParseMethod = raw_input("What is the name of the date parsing method needed? Hit Enter if no function is needed")

          outfile = open("output.txt", "a+")

          if(dateParseMethod != ""):
            outfile.write("self.{}.{} := {}(left.{});\n".format(model_name,ln_field,dateParseMethod,client_field))
          else:
            outfile.write("self.{}.{} := left.{};\n".format(model_name, ln_field, client_field))
          
          outfile.close()

        else:
          if(ln_field[-4:] == "-Map"):
            #while loop to cover bad Y/N for mapping
            while True:
              isMappingNeeded = raw_input("Does " + ln_field.replace("-Map", "") +
                                          " require additional mapping? Y/N")
              if (isMappingNeeded.upper() == 'Y'):
                  #so clearly, there's mapping to be done on this field pairing, pass in the ln_field, client_field and model_name
                  #into the MakeMapping script
                  #MakeMapping(model_name,client_field,ln_field)
                  #print("Whelp. We've got mapping now.")

                  #clear mapping tag
                  taglessln_field = ln_field.replace("-Map", "")
                  makeMapping.MakeMapping(model_name, client_field, taglessln_field)
                  break
              if(isMappingNeeded.upper() == 'N'):
                outfile = open("output.txt", "a+")
                outfile.write("self.{}.{} := left.{};\n".format(model_name, ln_field.replace("-Map", ""), client_field))
                outfile.close()
                break
          else:
            outfile = open("output.txt", "a+")
            outfile.write("self.{}.{} := left.{};\n".format(model_name, ln_field.replace("-Map", ""), client_field))
            outfile.close()
      break

#add footer for mapping projection
outfile = open("output.txt", "a+")
outfile.write("self.eligibility := left;\n")
outfile.write("self := left;\n")
outfile.write("self := [];\n")
outfile.write("));\n")
outfile.write("\n")
outfile.write("justdoit := output( outputDS,, ReformatName, overwrite, compressed, expire(30) );\n")
#the footers in the sequential won't exist if the file doesn't have a footer
if(doesFooterExist.upper() == "Y"):
  outfile.write("return sequential( HC_Data_Sharecare_Shared.Actions.isValidName(fname), HC_Data_Sharecare_Shared.Actions.reformatStart(fname), footerOut, footerAssert, justdoit, output(inputNoFooter[1..100]), HC_Data_Sharecare_Shared.Actions.reformatFinish(fname) );\n")
else:
  outfile.write("return sequential( HC_Data_Sharecare_Shared.Actions.isValidName(fname), HC_Data_Sharecare_Shared.Actions.reformatStart(fname), justdoit, output(inputDS[1..100]), HC_Data_Sharecare_Shared.Actions.reformatFinish(fname) );\n")
outfile.write("END;")
outfile.close()