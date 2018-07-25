def MakeMapping(data_model_name, raw_field_name, ln_field_name):
    #{self.data_model_name.ln_field_name
    #left.raw_field_name in [raw_values] => code_value

    #shower thoughts have elucided something for me - just take in the string and parse the list from there.
    #This means helper methods.

    #call method that will parse raw_values (i.e. the client's code) into an array of (probably) arrays store it in raw parse
    #blanks from the client code should be made into an indicator element - BLANK
    #values that are "NULL or Blank" should be converted to NULL
    #a set of values is to be in a comma delimited list of it's own

    #if somehow, the user missed the sizable gap between a Y and an N in got stuck here... I gotchu.
    while True:
      print("It's come to my attention that maybe "+ln_field_name+" doesn't need mapping and you fat fingered.")
      theChoice = raw_input("Does "+ln_field_name+" need mapping? Y/N")
      if(theChoice.upper() == "Y"): #if it does need mapping, no problemo proceed to mapping method
        break
      if(theChoice.upper() == "N"):  #if user DID fat finger... I gave them one chance to redeem themselves on the Y or N
        outfile = open("output.txt","a+")
        #so it HAS to just be a normal conversion
        outfile.write("self.{}.{} := left.{};\n".format(
                  data_model_name, ln_field_name, raw_field_name))
        outfile.close()
        return

    #input loop for invalid input
    while True:
      #input Client Code Column Here
      rawSpacedCodeSpace = raw_input("Input the space delimited field for the client code list e.g. 1 BLANK 2 3 4,5,6\n")

      rawCodeSpace = rawSpacedCodeSpace.split(" ")

      rawParsed = RawParser(rawCodeSpace)

      #call method that will parse the LN Codes, each translated to their repective constant in Shared.Constants
      #so pass in the ln_field_name in question to know which constants to lookup, then swap out the entry in the code_value
      #with the constant name c.[constant name].
      #e.g. having passed in 'Language Codes' [ln_field_name] and 'chi' [ln_code] should give 'c_Language_Chinese'
      #the only problem with this per se is right now, you've have to copy and past the dictionary in everytime...
      #but to be honest, that's no so bad, just have motepad doc of everything, go to what you need, and plug it in

      #input LN Code Column Here
      #There shouldn't be any blank rows, nor should there be any sets of codes on our end.
      spacedln_codes = raw_input("Input the space delimited field for the LN code list e.g. 1 2 3 4,5,6\n")

      ln_codes = spacedln_codes.split(" ")

      #input the ln_field_name in question to pass through i.e. the Field name in the mapping lookups (I hope to GOD they're standardized)
      #changing to introduce input
      #fieldToConvert = "Language Codes"
      fieldToConvert = raw_input("Input the constant name for the dictionary e.g. Language_Code You may need to look up the constant name in the dictionary in the code (under makeMapping, the CodeToConst method)\n")

      ln_codeParsed = CodeToConst(ln_codes, fieldToConvert)

      #finally we should have two sets, rawParsed and ln_codeParsed of equal length, for a zip up.
      #we'll need a "header" and "footer" for the bits not part of the mapping itself.
      #adding lines to add nessesary line to .txt

      #do a set length check to make sure everything lines up...
      if(len(rawParsed) != len(ln_codeParsed)):
        print("There is a problem with the inputted sets, you need to check your sets on this mapping.")
        print("Do not remove blanks and instead use BLANK for client fields. The client and LN sets should be equal in length.")
        print("FYI here's the number of fields we saw for the client list: "+len(rawParsed))
        print("FYI here's the number of fields we saw for the LN list: "+len(ln_codeParsed))
        print("Try again.")
      else:
        print("Good for mapping.")
        outfile = open("output.txt","a+")
        outfile.write("Trimmed_{} := STD.STR.ToUpperCase(TRIM(left.{}, LEFT, RIGHT));\n".format(raw_field_name, raw_field_name))
        outfile.write("self.{}.{} := MAP(\n".format(data_model_name, ln_field_name))

        #add in the for loop for zipping... in the format of:
        #print("Trimmed_{} in [{}] => c.{},".format(raw_field_name,rawParsed,ln_codeParsed))
        for client_code, ln_code in zip(rawParsed, ln_codeParsed):
            if (client_code == "\'Meow\'"):
                outfile.write("Trimmed_{} in [''] => c.{},\n".format(raw_field_name, ln_code))
                continue
            if (client_code != "\'BLANK\'"):
                outfile.write("Trimmed_{} in [{}] => c.{},\n".format(raw_field_name,client_code, ln_code))
                continue
            else:
                continue

        #need to add the isValid statement... I'd argue that can land in the dictionary, but that would cancel out the zip, so
        #It might be better to hardcode here

        #Input isValid constant here for field if it exists. If it doesn't, leave blank.
        #this is the "anything other than what's listed above, right? Otherwise, I can put up a check for that string literal...
        #but it looks like we don't have a base case for "NF" besides the isValid.

        #isvalid check isn't nessesary as of discussion with Richard over it's nature 
        #(it's analogous to self := Left as a catch all)
        #isValid = "IsValidLanguage"

        #if (isValid != ""):
        #    print("Trimmed_{} in c.{} => c.c_Universal_Data_Not_Valid,".format(
        #        raw_field_name, isValid))

        outfile.write("left.{}\n".format(raw_field_name))
        outfile.write(");\n")
        outfile.close()
        break


def RawParser(rawCodes):
    #so, essentially, all that's needed here is to find entries that need more quotes in their life
    #e.g. for Language Code in SCCareFirst_v1.6:
    #"146, 147, 148, Null/Blank" needs to be "\'146\', \'147\', \'148\', \'\'"
    returningSet = []
    for raw in rawCodes:
        # rawSampleNoSpace = raw.replace(" ","")
        # rawSampleNoSpaceCapped = rawSampleNoSpace.upper()
        # rawAddingLeadTrailQuote = "\'"+rawSampleNoSpaceCapped+"\'"
        # rawQuoteWithComma = rawAddingLeadTrailQuote.replace(",","\',\'")
        rawQuoteWithComma = raw.replace(" ", "").upper().replace(
            ",", "\',\'")#.replace("NULL", "Meow")
        #add if to check specifically for a lone NULL
        if(rawQuoteWithComma == "\'NULL\'"):
          rawQuoteWithComma = "Meow"
        else:
          rawQuoteWithComma = rawQuoteWithComma.replace("NULL","")
        rawAddingLeadTrailQuote = "\'" + rawQuoteWithComma + "\'"
        returningSet.append(rawAddingLeadTrailQuote)
    return returningSet


def CodeToConst(ln_codes, field):
    #for here it should just be loop through the input list as if through a dictionary to make the return list.
    #this is really the only part that the user might need to jump through substantial hoops
    #I've got some ways around it, name putting a unique tag for each field in front of the key?
    #e.g. 'chi' is input as 'language_code_chi' due to searching for [field+codes] in the dictionary
    #This would consolidate all constant dictionaries into one and only have the routine defined once
    #AMD has been created and is ready (probably) for implementation.

    #AMD idea is go, need to add in unique constants for each data model but for now, it's good for eligibility

    #for now though... I guess I'll have the if block (Proof of Concept)
    #these dictionaries will have to be case-specific, kind of obvious, but I'm just reminding myself

    #DICTIONARY SPACE
    #so far, I've got the constants in eligibility - will eventually need to do it for the other data models too
    #this will probably involve using another tag to indicate unique constants? Maybe? 
    #best case is the unique constants are uniquely named too
  Absolutely_Massive_Dictionary = {
    #from Shared
    #Universal Constants
    'NP' : "c_Universal_Data_Not_Provided",
    'NF' : "c_Universal_Data_Not_Valid",
    #Environment_Indicator
    'Environment_Indicator-T' : "c_Enviroment_Indicator_Test",
    'Environment_Indicator-P' : "c_Enviroment_Indicator_Production",
    #Record_Type
    'Record_Type-HDR' : "c_Record_Type_Header",
    'Record_Type-DTL' : "c_Record_Type_Detail",
    'Record_Type-TRL' : "c_Record_Type_Trailer",
    #File_Type
    'File_Type-001' : "c_File_Type_Eligibility_File",
    'File_Type-002' : "c_File_Type_Detail",
    'File_Type-003' : "c_File_Type_Trailer",
    #Employment_Status_Code
    'Employment_Status_Code-AC' : "c_Employment_Status_Code_Active",
    'Employment_Status_Code-AO' : "c_Employment_Status_Code_Active_Military_Overseas",
    'Employment_Status_Code-AU' : "c_Employment_Status_Code_Active_Military_USA",
    'Employment_Status_Code-FT' : "c_Employment_Status_Code_Full_Time",
    'Employment_Status_Code-L1' : "c_Employment_Status_Code_Leave_of_Absence",
    'Employment_Status_Code-PT' : "c_Employment_Status_Code_Part_Timne",
    'Employment_Status_Code-RT' : "c_Employment_Status_Code_Retired",
    'Employment_Status_Code-TE' : "c_Employment_Status_Code_Terminated",
    'Employment_Status_Code-U' : "c_Employment_Status_Code_Unknown",
    #Group1 codes don't seem... standard? Leaving them out for now
    #Market_Type
    'Market_Type-GRP' : "c_Market_Type_Group",
    'Market_Type-IND' : "c_Market_Type_Individual",
    #Plan_Category
    'Plan_Category-HMO' : "c_Plan_Category_HealthManagementOrganization",
    'Plan_Category-PPO' : "c_Plan_Category_PreferredProviderOrganization",
    'Plan_Category-EPO' : "c_Plan_Category_ExclusiveProviderOrganization",
    'Plan_Category-POS' : "c_Plan_Category_PointOfService",
    #Plan_Type
    'Plan_Type-01' : "c_Plan_Type_Medical",
    'Plan_Type-02' : "c_Plan_Type_Dental",
    'Plan_Type-03' : "c_Plan_Type_Vision",
    'Plan_Type-04' : "c_Plan_Type_Pharmacy",
    #Gender-
    'Gender-01' : "c_Gender_Unknown",
    'Gender-02' : "c_Gender_Male",
    'Gender-03' : "c_Gender_Female",
    #Relationship_Code-
    'Relationship_Code-01' : "c_Relationship_Code_Insured",
    'Relationship_Code-02' : "c_Relationship_Code_Spouse",
    'Relationship_Code-08' : "c_Relationship_Code_Employee",
    'Relationship_Code-09' : "c_Relationship_Code_Unknown",
    'Relationship_Code-16' : "c_Relationship_Code_SponsoredDevelopment",
    'Relationship_Code-20' : "c_Relationship_Code_LifePartner",
    'Relationship_Code-21' : "c_Relationship_Code_Self",
    'Relationship_Code-22' : "c_Relationship_Code_Other",
    'Relationship_Code-23' : "c_Relationship_Code_Adult_Dependent",
    'Relationship_Code-24' : "c_Relationship_Code_Company_Spouse",
    #Eligibility_End_Date
    'Eligibility_End_Date-99991231' : "c_Eligibility_End_Date_HighValue",
    #Marital_Status-
    'Marital_Status-S' : "c_Marital_Status_Single",
    'Marital_Status-M' : "c_Marital_Status_Married",
    'Marital_Status-P' : "c_Marital_Status_LifePartner",
    'Marital_Status-X' : "c_Marital_Status_LegallySeparated",
    'Marital_Status-D' : "c_Marital_Status_Divorced",
    'Marital_Status-W' : "c_Marital_Status_Widowed",
    'Marital_Status-U' : "c_Marital_Status_Unknown",
    #Funding_Type-
    'Funding_Type-01' : "c_Funding_Type_FullyInsured",
    'Funding_Type-02' : "c_Funding_Type_SelfInsured",
    #Benefit_Status_Code-
    'Benefit_Status_Code-A' : "c_Benefit_Status_Code_Active",
    'Benefit_Status_Code-C' : "c_Benefit_Status_Code_COBRA",
    'Benefit_Status_Code-S' : "c_Benefit_Status_Code_Surviving_Spouse",
    #Cobra_Medical_Indicator-
    'Cobra_Medical_Indicator-C' : "c_Cobra_Medical_Indicator_Cobra",
    'Cobra_Medical_Indicator-P' : "c_Cobra_Medical_Indicator_Participating",
    #Ethnicity-
    'Ethnicity-01' : "c_Ethnicity_Hispanic_or_Latino",
    'Ethnicity-02' : "c_Ethnicity_Not_Hispanic_or_Latino",
    #Race-
    'Race-A' : "c_Race_Asian_or_Pacific_Islander",
    'Race-B' : "c_Race_Black",
    'Race-C' : "c_Race_Caucasian",
    'Race-D' : "c_Race_Subcontinent_Asian_American",
    'Race-E' : "c_Race_Other_Race",
    'Race-F' : "c_Race_Asian_Pacific_American",
    'Race-G' : "c_Race_Native_American",
    'Race-H' : "c_Race_Hispanic",
    'Race-I' : "c_Race_American_Indian_or_Alaskan_Native",
    'Race-J' : "c_Race_Native_Hawaiian",
    'Race-N' : "c_Race_Non_Hispanic_Black",
    'Race-O' : "c_Race_Non_Hispanic_White",
    'Race-P' : "c_Race_Pacific_Islander",
    #Batch_Type-
    'Batch_Type-R' : "c_BatchType_Full_Refresh",
    'Batch_Type-U' : "c_BatchType_Delta_Updates",
    'Batch_Type-D' : "c_BatchType_Delete",
    #Person_Number-
    'Person_Number-01' : "c_PersonNumber_Primary",
    'Person_Number-02' : "c_PersonNumber_Spouse",
    'Person_Number-03' : "c_PersonNumber_DepOne",
    'Person_Number-04' : "c_PersonNumber_DepTwo",
    'Person_Number-05' : "c_PersonNumber_DepThree",
    'Person_Number-06' : "c_PersonNumber_DepFour",
    'Person_Number-07' : "c_PersonNumber_DepFive",
    'Person_Number-08' : "c_PersonNumber_DepSix",
    'Person_Number-09' : "c_PersonNumber_DepSeven",
    'Person_Number-10' : "c_PersonNumber_DepEight",
    'Person_Number-11' : "c_PersonNumber_DepNine",
    'Person_Number-12' : "c_PersonNumber_DepTen",
    #Country_Code-
    'Country_Code-US' : "c_Country_US",
    'Country_Code-CA' : "c_Country_Canada",
    #Language_Code-
    'Language_Code-chi' : "c_Language_Chinese",
    'Language_Code-spa' : "c_Language_Spanish",
    'Language_Code-eng' : "c_Language_English",
    'Language_Code-hin' : "c_Language_Hindi",
    'Language_Code-ara' : "c_Language_Arabic",
    'Language_Code-por' : "c_Language_Portugese",
    'Language_Code-ben' : "c_Language_Bengali",
    'Language_Code-rus' : "c_Language_Russian",
    'Language_Code-jap' : "c_Language_Japanese",
    'Language_Code-pun' : "c_Language_Punjabi",
    'Language_Code-fre' : "c_Language_French",
	  'Language_Code-ger' : "c_Language_German",
	  'Language_Code-mal' : "c_Language_Malay",
	  'Language_Code-Jav' : "c_Language_Javanese",
	  'Language_Code-tel' : "c_Language_Telugu",
	  'Language_Code-kor' : "c_Language_Korean",
	  'Language_Code-vie' : "c_Language_Vietnamese",
	  'Language_Code-ita' : "c_Language_Italian",
    #from ExternalEvents
    #Event_Type-
    'Event_Type-A' : "Activity_Event",
    'Event_Type-C' : "Condition_Event",
    'Event_Type-CL' : "Classification_Event",
    #from Labs
    
  }
  #END OF DICTIONARY SPACE

  returningSet = []

  for codes in ln_codes:
    #covering for the universal errors since in this proof of concept model, the dictionaries will be specialized
    if (codes == 'NP'):
      returningSet.append("c_Universal_Data_Not_Provided")
      continue
    if (codes == 'NF'):
      returningSet.append("c_Universal_Data_Not_Valid")
      continue
    else:
      lookup = field+"-"+codes
      returningSet.append(Absolutely_Massive_Dictionary[lookup])

  return returningSet

