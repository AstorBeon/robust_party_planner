import json
import random
from io import StringIO

import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
from fpdf import FPDF, XPos, YPos
import base64
from tempfile import NamedTemporaryFile

from Supports import create_detailed_map, extract_coordinates_and_address, image_to_pdf, get_static_map

#image = Image.open('dominik_cut.png')

VERSION = "1.5.1"
transport_min=0
transport_max=0
accom_min=0
accom_max=0
foods_min =0
foods_max=0
PARTYTYPE = ""
NAME = ""


st.set_page_config(page_title=f"Party planner - cost breakdown calculator",layout="wide")


file_upload = st.sidebar.file_uploader("Upload prepared data",type=["astor"])

#Leave popup
st.markdown("""
<script>
window.addEventListener("beforeunload", function (e) {
    e.preventDefault();
    e.returnValue = '';
});
</script>
""", unsafe_allow_html=True)


@st.dialog("Enter basic details")
def popup_form():
    st.write("Please fill in your information:")

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Name")
    with col2:
        partytype = st.selectbox("Party type",["Bachelors party","Hen party","Birthday","Team building","Event","Other"])
        if partytype == "Other":
            custom_value = st.text_input("Enter your own value")
            final_value = custom_value
        else:
            final_value = partytype


    st.divider()

    if st.button("Submit"):

        st.session_state["NAME"] = name
        st.session_state["PARTYTYPE"] = final_value

        st.rerun()

if "NAME" not in st.session_state:
    popup_form()
else:
    NAME = st.session_state["NAME"]
    PARTYTYPE = st.session_state["PARTYTYPE"]

if file_upload is not None:
    stringio = StringIO(file_upload.getvalue().decode("utf-8"))
    string_data = stringio.read()

    upload_json = json.loads(string_data)

    #additional check for version
    if VERSION != upload_json["VERSION"]:
        st.warning(f"File you're loading was generated using version {upload_json['VERSION']} while current version is {VERSION}."
                   f"This can cause errors while loading data")

    st.session_state["NAME"] = upload_json["General"][0]
    st.session_state["PARTYTYPE"] = upload_json["General"][1]
    st.session_state["limit"] = upload_json["General"][2]
    st.session_state["Transportation"]["option"]=upload_json["Transport"]["transport_type"]
    try:
        st.session_state["Transportation"]["is_adv"]=upload_json["Transport"]["is_adv"]
    except:
        pass
    #st.session_state["Transportation"]["deviation"] = upload_json["Transport"]["deviation"]
    try:
        st.session_state["Transportation"]["cost_of_transport_on_site"] = upload_json["Transport"]["cost_of_transport_on_site"]
        st.session_state["Transportation"]["cost_of_transport"] = upload_json["Transport"]["cost_of_transport"]

    except Exception as e:
        pass
    try:
        st.session_state["Transportation"]["cost_of_transport_fuel"] = upload_json["Transport"]["cost_of_transport_fuel"]
    except Exception:
        pass
    try:
        st.session_state["Transportation"]["Liters per 100km"] = upload_json["Transport"]["Liters per 100km"]
        st.session_state["Transportation"]["Cost of single liter"] = upload_json["Transport"]["Cost of single liter"]
        st.session_state["Transportation"]["Distance to drive"] = upload_json["Transport"]["Distance to drive"]
        st.session_state["Transportation"]["Highway fees"] = upload_json["Transport"]["Highway fees"]
        st.session_state["Transportation"]["Notes"] = upload_json["Transport"]["Note"]

    except Exception:
        pass

    try:
        st.session_state["Transportation"]["cost_of_local_tickets"] = upload_json["Transport"]["cost_of_local_tickets"]
    except Exception:
        pass

    st.session_state["Accommodation"]["accommodation_cost"] = upload_json["Accommodation"]["accommodation_cost"]
    st.session_state["Accommodation"]["link"] = upload_json["Accommodation"]["link"]
    st.session_state["Accommodation"]["deviation"] = upload_json["Accommodation"]["deviation"]
    st.session_state["Accommodation"]["Notes"] = upload_json["Accommodation"]["Notes"]

    st.session_state["Food_drinks"]["Cost_food"] = upload_json["Food_drinks"]["Cost_food"]
    st.session_state["Food_drinks"]["Cost_drinks"] = upload_json["Food_drinks"]["Cost_drinks"]
    st.session_state["Food_drinks"]["Days"] = upload_json["Food_drinks"]["Days"]
    st.session_state["Food_drinks"]["deviation"] = upload_json["Food_drinks"]["deviation"]
    st.session_state["Food_drinks"]["Notes"] = upload_json["Food_drinks"]["Notes"]


    st.session_state["activities"]["list"] = upload_json["Activities"]["list"]
    st.session_state["activities"]["Notes"] = upload_json["Activities"]["Notes"]
    st.session_state["Other"]["general_notes"] = upload_json["Other"]["general_notes"]
    pass


if "is_new_activity_open" not in st.session_state:
    st.session_state['is_new_activity_open']=False

random_activities=["Washing my car","Doing pushups","Drinking questionable liquids","Trying to lick own elbow",
                   "Petting dogs","Battling ancient evil","Watching cartoons","Digging tunnel to China","Cracking joints"]

if "NAME" not in st.session_state:
    st.session_state["NAME"] = NAME

if "PARTYTYPE" not in st.session_state:
    st.session_state["PARTYTYPE"] = "Bachelors"

if st.session_state['NAME']=='' and st.session_state['PARTYTYPE']=='':
    st.title(f"Some event - Cost breakdown")
else:
    st.title(f"{st.session_state['NAME']}'s {PARTYTYPE} party - Cost breakdown")

gen_col1, gen_col2 = st.columns(2)
with gen_col1:
    NAME = st.text_input("Name of Person of the hour:" , st.session_state["NAME"])
with gen_col2:
    PARTYTYPE = st.text_input("Type of party (ex. Bachelors):" , st.session_state["PARTYTYPE"])



if NAME:
    st.session_state["NAME"] = NAME

if PARTYTYPE:
    st.session_state["PARTYTYPE"] = PARTYTYPE

if "limit" not in st.session_state:
    st.session_state["limit"] = 100

limit= st.number_input('Amount to be spent (initial assumption)', st.session_state["limit"])
st.subheader('Transportation')

#todo add loading from session state
if "Transportation" not in st.session_state:

    #Initializing all fields with default values
    st.session_state["Transportation"]={}
    st.session_state["Transportation"]["option"]="Train"
    st.session_state["Transportation"]["cost_of_transport"] = 0
    st.session_state["Transportation"]["cost_of_local_tickets"] = 0
    st.session_state["Transportation"]["cost_of_transport_on_site"] = 0
    st.session_state["Transportation"]["cost_of_transport_fuel"] = 0
    st.session_state["Transportation"]["Liters per 100km"] = 0
    st.session_state["Transportation"]["Cost of single liter"] = 0
    st.session_state["Transportation"]["Distance to drive"] = 0
    st.session_state["Transportation"]["Highway fees"] = 0
    st.session_state["Transportation"]["Notes"] = "None"
    st.session_state["Transportation"]["is_adv"] = False
    st.session_state["Transportation"]["deviation"] = 0

if "Accommodation" not in st.session_state:
    st.session_state["Accommodation"]={}
    st.session_state["Accommodation"]["accommodation_cost"] = 0
    st.session_state["Accommodation"]["link"] = ''
    st.session_state["Accommodation"]["deviation"] = 0
    st.session_state["Accommodation"]["Notes"] = "None"
#todo add initial values for rest of categories + load them above

if "Food_drinks" not in st.session_state:
    st.session_state["Food_drinks"] = {}
    st.session_state["Food_drinks"]["Cost_food"] = 0
    st.session_state["Food_drinks"]["Cost_drinks"] = 0
    st.session_state["Food_drinks"]["Days"] = 1
    st.session_state["Food_drinks"]["deviation"] = 0
    st.session_state["Food_drinks"]["Notes"] = "None"

if "activities" not in st.session_state:
    st.session_state["activities"]={}
    st.session_state["activities"]["list"]=[]
    st.session_state["activities"]["Notes"]="None"
    st.session_state['activities_objs'] = []

if "Other" not in st.session_state:
    st.session_state["Other"] = {}
    st.session_state["Other"]["general_notes"] = "None"

    option = st.selectbox(
         'How will we travel?',
         ('Train', 'Car','No travel - staying in city'))
else:
    options = [st.session_state["Transportation"]["option"]]
    for o in ['Train', 'Car','No travel - staying in city']:
        if o not in options:
            options.append(o)
    option = st.selectbox(
         'How will we travel?',
         options)


trans_col1, trans_col2 = st.columns(2)
if option == "Train":

    with trans_col1:
        cost_of_transport = st.number_input('Cost of the ticket (two ways)', st.session_state["Transportation"]["cost_of_transport"])
    with trans_col2:
        cost_of_transport_on_site= st.number_input('Cost of transportation on site', st.session_state["Transportation"]["cost_of_transport_on_site"])
    transport_total = int(cost_of_transport) + int(cost_of_transport_on_site)
elif option == 'No travel - staying in city':
    cost_of_transport = st.text_input('Cost of local tickets', st.session_state["Transportation"]["cost_of_local_tickets"])
else:
    adv = st.checkbox('Advanced transport calculations',st.session_state["Transportation"]["is_adv"])

    if not adv:
        with trans_col1:
            cost_of_transport_fuel = st.text_input('Cost of fuel:', st.session_state["Transportation"]["cost_of_transport_fuel"])
        with trans_col2:
            cost_of_transport_on_site = st.text_input('Cost of transportation on site', st.session_state["Transportation"]["cost_of_transport_on_site"])
        transport_total = int(cost_of_transport_fuel) + int(cost_of_transport_on_site)
    else:
        #Advanced cost calculating for car
        with trans_col1:
            cost_of_transport_litres_per_100km = st.number_input('Litres of fuel 100km:', st.session_state["Transportation"]["Liters per 100km"])
            cost_of_transport_cost_of_litre = st.number_input("Cost of single litre:", st.session_state["Transportation"]["Cost of single liter"])
            cost_of_transport_length = st.number_input('Length of whole route(km) - two ways:', st.session_state["Transportation"]["Distance to drive"])
        with trans_col2:
            cost_of_transport_highway_fee = st.number_input('Cost of highway fees:', st.session_state["Transportation"]["Highway fees"])
            cost_of_transport_on_site = st.number_input('Cost of transportation on site', st.session_state["Transportation"]["cost_of_transport_on_site"])

        transport_total = float(cost_of_transport_highway_fee) + \
                          float(cost_of_transport_length) / 100 * float(cost_of_transport_cost_of_litre) *\
                          float(cost_of_transport_litres_per_100km) + float(cost_of_transport_on_site)

        cost_of_transport_deviation = st.number_input('Deviation/Reserve (%):', st.session_state["Transportation"]["deviation"])


        cost_of_transport_deviation_calculation = transport_total if cost_of_transport_deviation==0 else transport_total/int(cost_of_transport_deviation)
        st.markdown("""
        <style>
        .big-font {
            font-size:20px !important;
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown(f'<p class="big-font">Including {cost_of_transport_deviation}% deviation, total cost of transport is: ---> {transport_total + transport_total/float(cost_of_transport_deviation if cost_of_transport_deviation!=0 else 1)}</p>', unsafe_allow_html=True)
notes_transportation = st.text_input("Notes for transportation: ","None")
st.subheader('Accommodation')
acom_col1, acom_col2 = st.columns(2)
with acom_col1:
    cost_of_accommodation = st.number_input('Cost of accommodation(total):', st.session_state["Accommodation"]["accommodation_cost"])
with acom_col2:
    cost_of_accommodation_deviation = st.number_input('Deviation/Reserve(%):', st.session_state["Accommodation"]["deviation"])
st.markdown("""
<style>
.big-font {
    font-size:20px !important;
}
</style>
""", unsafe_allow_html=True)

accommodation_link = st.text_input('Link:',
                                        st.session_state["Accommodation"]["link"])
acom_map=None
if accommodation_link:
    lat,lon,address = extract_coordinates_and_address(accommodation_link)
    if lat is not None:
        st.write("Name: {}".format(address))
        get_static_map(lat, lon)
        acom_map = st.pydeck_chart(create_detailed_map(lat,lon))

        st.success(f"Coordinates extracted!")
    else:
        st.error("Failed to extract coordinates :(")


try:
    accommodation_total_deviation_calculation =int(cost_of_accommodation) / float(cost_of_accommodation_deviation)
    accom_min=int(cost_of_accommodation)-accommodation_total_deviation_calculation
    accom_max=int(cost_of_accommodation)+accommodation_total_deviation_calculation
except Exception:
    accommodation_total_deviation_calculation=0
    accom_min,accom_max=int(cost_of_accommodation),int(cost_of_accommodation)
if accommodation_total_deviation_calculation==0:
    st.markdown(
        f'<p class="big-font">Total cost of accommodation is: ---> {cost_of_accommodation}</p>',
        unsafe_allow_html=True)
else:
    st.markdown(
        f'<p class="big-font">Including {cost_of_accommodation_deviation}% deviation, total cost of accommodation is between : ---> {int(cost_of_accommodation)-accommodation_total_deviation_calculation} and {int(cost_of_accommodation)+accommodation_total_deviation_calculation}</p>',
        unsafe_allow_html=True)

notes_accommodation = st.text_input("Notes for accommodation: ",st.session_state["Accommodation"]["Notes"])
st.subheader('Food & Drinks')
food_col1, food_col2, food_col_3 = st.columns(3)
with food_col1:
    cost_of_food = st.number_input('Cost of food', st.session_state["Food_drinks"]["Cost_food"])
with food_col2:
    cost_of_drinks = st.number_input('Cost of drinks (alc)', st.session_state["Food_drinks"]["Cost_drinks"])
with food_col_3:
    amount_of_days = st.number_input('Amount of days', st.session_state["Food_drinks"]["Days"])
total_cost_foods_drinks = (int(cost_of_food) + int(cost_of_drinks))*amount_of_days
cost_of_food_deviation = st.number_input('Deviation(%):', st.session_state["Food_drinks"]["deviation"])

try:
    foods_total_deviation_calculation =0  if cost_of_food_deviation ==0 else total_cost_foods_drinks/ float(cost_of_food_deviation)
    foods_min=total_cost_foods_drinks-foods_total_deviation_calculation
    foods_max=total_cost_foods_drinks+foods_total_deviation_calculation
except Exception:
    foods_total_deviation_calculation=0
    foods_min,foods_max=total_cost_foods_drinks,total_cost_foods_drinks
if foods_total_deviation_calculation==0:
    st.markdown(
        f'<p class="big-font">Total cost of foods and drinks is: ---> {total_cost_foods_drinks}</p>',
        unsafe_allow_html=True)
else:
    st.markdown(
        f'<p class="big-font">Including {cost_of_food_deviation}% deviation, total cost of foods and drinks is between : ---> {int(total_cost_foods_drinks)-foods_total_deviation_calculation} and {int(total_cost_foods_drinks)+foods_total_deviation_calculation}</p>',
        unsafe_allow_html=True)

notes_food_drinks = st.text_input("Notes for foods & drinks: ",st.session_state["Food_drinks"]["Notes"])


#todo activities
st.subheader("Activities")

def generate_knowledge_summary():
    pass
count=0
initial = True

def delete_from_activities(index):
    if initial:

        return
    del st. session_state['activities'][index]


st.markdown("""
    <style>
        .centered {
            margin-top:9%;
            font-size: 20px;
        }
    </style>
""", unsafe_allow_html=True)

for rec in st.session_state['activities']["list"]:
    col_1, col_2, col_3, col_4 = st.columns(4)
    with col_1:
        st.markdown(f'<div class="centered">{rec[0]}</div>', unsafe_allow_html=True)

    with col_2:
        x = st.number_input("Cost:",rec[1])
    with col_3:
        y = st.text_input("Link", rec[2])
    st.session_state['activities_objs'].append((x,y))
    #st.session_state['activities_objs'].append(x)
    st.session_state['activities']['list'][count]=(rec[0],x,y)



    with col_4:
        st.text("   ")
        st.text("   ")
        st.button(f"""DELETE -\n {rec[0]}""",on_click=delete_from_activities,args=(count,))
    count+=1
#notes_activities = st.text_input("Notes for activities","None")

def add_activity_panel():
    st.session_state['is_new_activity_open']=True

if (st.session_state['is_new_activity_open']):
    if "temp new activity" not in st.session_state:
        st.session_state["temp new activity"]=random.choice(random_activities)
    act_name = st.text_input(f"New activity name: ",st.session_state["temp new activity"],)

    x = st.number_input("Cost:",0)

    y = st.text_input("Link:",'')


    def add_activity():
        st.write(act_name)
        if act_name:
            st.write(act_name)
        st.session_state['activities']["list"].append((act_name,x,y))
        #print(f"Adding: {st.session_state['activities']['list']}")
        st.session_state['activities_objs'].append(act_name)
        st.session_state['is_new_activity_open'] = False


    st.button("Approve new activity",on_click=add_activity)
st.button("Add new activity",on_click=add_activity_panel)

notes_activities = st.text_input("Notes for activities: ","None")
initial=False

activities_cost = sum([int(x[1]) for x in st.session_state['activities']["list"]])

total_cost = transport_total + activities_cost+int(cost_of_accommodation) + total_cost_foods_drinks

st.markdown("""
<style>
.big-font-res {
    font-size:60px !important;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

def generate_knowledge_summary():
    st.subheader("Summary:")
    knowledge_summary =  f"Way of transportation: {option} ->"

    try:
        #cost_of_transport_deviation_calculation
        transport_min =transport_total - cost_of_transport_deviation_calculation
        transport_max = transport_total + cost_of_transport_deviation_calculation
        knowledge_summary += f" {round(transport_min,2)} <-> {round(transport_max,2)}<br>"


    except Exception:
        knowledge_summary += f"{transport_total}<br>"
        transport_min,transport_max = transport_total,transport_total

    knowledge_summary+=f"Accommodation -> "
    if accommodation_total_deviation_calculation !=0:
        accom_min = int(cost_of_accommodation)-accommodation_total_deviation_calculation
        accom_max=int(cost_of_accommodation)+accommodation_total_deviation_calculation
        knowledge_summary+=f"{accom_min} <-> {accom_max}<br>"
    else:
        knowledge_summary+=f"{cost_of_accommodation}<br>"

    knowledge_summary+=f"Foods & drinks -> "
    if(foods_total_deviation_calculation!=0):
        foods_min = total_cost_foods_drinks-foods_total_deviation_calculation
        foods_max = total_cost_foods_drinks+foods_total_deviation_calculation
        knowledge_summary+=f"{foods_min} <-> {foods_max}<br>"
    else:
        knowledge_summary+=f"{total_cost_foods_drinks}<br>"

    knowledge_summary+=f"Activities -> {activities_cost}:<br>"
    for activity in st.session_state['activities']["list"]:


        knowledge_summary += f">>>{activity[0]} -> {activity[1]}<br>"

    #knowledge_summary+=f"Total for activities is: {activities_cost}"
    return knowledge_summary

#knowledge_summary=generate_knowledge_summary()
def show_summary():
    #st.write(generate_knowledge_summary())
    st.markdown(
    f'<p class="big-font">{generate_knowledge_summary()}</p>',
    unsafe_allow_html=True)


#st.button(f"Generate sumary!",on_click=show_summary)
show_summary()
true_total_cost = transport_total + int(cost_of_accommodation) + total_cost_foods_drinks+activities_cost
addition_for_bach = st.number_input(f"Percentage added for bachelor (cos  {NAME} doesn't pay)",10)
true_total_cost *= 1+float(addition_for_bach)/100

min_costs=foods_min + accom_min + transport_min + int(activities_cost)

min_costs*=1+float(addition_for_bach)/100

max_costs=foods_max + transport_max + accom_max + int(activities_cost)
max_costs*=1+float(addition_for_bach)/100

if (min_costs!=max_costs):
    st.markdown(
        f'<p class="big-font-res">Total cost is between {round(min_costs,2)} and {round(max_costs,2)}</p>',
        unsafe_allow_html=True)
else:
    st.markdown(
    f'<p class="big-font-res">Total cost is {true_total_cost}</p>',
    unsafe_allow_html=True)


if (min_costs+max_costs)/2>int(limit):
    st.error(f"Including all deviations, total cost WILL be higher than planned - from {round(min_costs-int(limit),2)} up to {round(max_costs-int(limit),2)} over the limit")
elif max_costs>int(limit):
    st.warning(
        f"Including all deviations, total cost might be higher than planned - up to {round(max_costs - int(limit),2)} over the limit")
else:
    st.success("It seems like all costs are going to be within initial assumption!")


#st.markdown("<br>",unsafe_allow_html=True)

notes_general = st.text_input("General notes for whole party: ",st.session_state["Other"]["general_notes"])


def create_download_link(val, filename):
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.pdf">Click here to download summary (experimental)</a>'


def export_pdf_data():
    #st.balloons()

    pdf = FPDF('P', 'mm', 'A4')
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 25)
    pdf.cell(190, 10, f'{NAME}\'s party cost breakdown (per person)', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font('Helvetica', 'B', 15)
    pdf.ln(5)
    pdf.cell(40, 10, f'Transport: {option}', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_font('Helvetica', '', 12)

    if "No travel" not in option:
        if option == "Train":
            pdf.cell(70, 10, f'Cost of ticket (two ways): {cost_of_transport}', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.cell(70, 10, f'Cost of transport on site: {cost_of_transport_on_site}', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        else:
            if not adv:
                pdf.cell(70, 10, f'Cost of fuel (two ways): {cost_of_transport_fuel}', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                pdf.cell(70, 10, f'Cost of transport on site: {cost_of_transport_on_site}', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            else:
                try:
                    pdf.cell(70, 10, f'Liters per 100km: {cost_of_transport_litres_per_100km}', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

                    pdf.cell(70, 10, f'Cost of single liter: {cost_of_transport_cost_of_litre}', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.cell(70, 10, f'Distance to drive: {cost_of_transport_length}', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.cell(70, 10, f'Highway fees: {cost_of_transport_highway_fee}', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                    pdf.cell(70, 10, f'Cost of transport on site: {cost_of_transport_on_site}', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
                except Exception:
                    pass

        pdf.cell(70, 10, f'Total travel cost: {transport_total}', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(70, 10, f"Notes: {notes_transportation}",0,new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(5)

        #accommodation
        pdf.set_font('Helvetica', 'B', 15)

        pdf.cell(40, 10, f'Accommodation:', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font('Helvetica', '', 12)
        if acom_map:
            pdf.cell(70, 10, f'{address}', 0, new_x=XPos.LMARGIN,
                 new_y=YPos.NEXT)

            #get_static_map(lat,lon)
            pdf.image("map.png", x=10, y=100, w=180)
            pass
            pdf.ln(130)

        if cost_of_accommodation_deviation == 0:
            pdf.cell(70, 10, f'Total cost of accommodation: {cost_of_accommodation}', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        else:
            pdf.cell(70, 10, f'Total cost of accommodation: {cost_of_accommodation*(1-cost_of_accommodation_deviation)}-{cost_of_accommodation*(1+cost_of_accommodation_deviation)}', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        pdf.cell(70, 10, f'Accommodation cost deviation: {cost_of_accommodation_deviation}%', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(40, 10, f'Notes: {notes_accommodation}', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.add_page()
        pdf.set_font('Helvetica', 'B', 15)
        pdf.cell(40, 10, f'Foods & drinks:', 0,new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font('Helvetica', '', 12)
        pdf.cell(70, 10, f"Cost of food: {cost_of_food}", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(70, 10, f"Cost of drinks: {cost_of_drinks}", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        if cost_of_food_deviation==0:
            pdf.cell(70, 10, f"Total cost of f&d: {(cost_of_drinks+cost_of_food)*(1-cost_of_food_deviation)} - {(cost_of_drinks+cost_of_food)*(1-cost_of_food_deviation)}", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        else:
            pdf.cell(70, 10, f"Total cost of f&d: {(cost_of_drinks+cost_of_food)}", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(70, 10, f"Deviation of cost of food and drinks: {cost_of_food_deviation}%", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        pdf.ln(5)
        pdf.set_font('Helvetica', 'B', 15)
        pdf.cell(40, 10, f'Activities:', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font('Helvetica', '', 12)
        #for act, actobj in zip(st.session_state["activities"],st.session_state["activities_objs"]):
        for act in st.session_state["activities"]["list"]:
            pdf.cell(70, 10, f"{act[0]}: {act[1]}", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

        pdf.cell(70, 10, f"Notes: {notes_activities}", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(10)
        pdf.set_font('Helvetica', 'B', 15)
        pdf.cell(40, 10, f'Total cost (including deviations and general additional cost',0,new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.cell(40,10,f'of the main person - {addition_for_bach}%) is:'
                         f'{round(min_costs,2)} - {round(max_costs,2)}', 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font('Helvetica', '', 12)
        pdf.cell(70, 10, f"General notes: {notes_general}", 0, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    #html = create_download_link(pdf.output(dest="S").encode("latin-1"), "test")
        #st.balloons()
    return pdf
    #st.markdown({html}, unsafe_allow_html=True)
    #st.button("Experimental", on_click=lambda x: html.cl)

def export_json_data():
    # st.balloons()
    ret_dict = {"General":[NAME,PARTYTYPE,limit],
                "Transport":{
                    "transport_type":option,

                },
                "Version":"1.4"
                }


    if "No travel" not in option:
        if option == "Train":
            ret_dict["Transport"]["cost_of_transport"] = cost_of_transport
            ret_dict["Transport"]["cost_of_transport_on_site"] = cost_of_transport_on_site
        elif option == "Car":
            ret_dict["Transport"]["is_adv"] = adv
            if not adv:
                ret_dict["Transport"]["cost_of_transport_fuel"] = cost_of_transport_fuel
                ret_dict["Transport"]["cost_of_transport_on_site"] = cost_of_transport_on_site
            else:
                try:
                    ret_dict["Transport"]["cost_of_transport_on_site"] = cost_of_transport_on_site
                    ret_dict["Transport"]['Liters per 100km']= cost_of_transport_litres_per_100km
                    ret_dict["Transport"]['Cost of single liter']=cost_of_transport_cost_of_litre
                    ret_dict["Transport"]['Distance to drive']=cost_of_transport_length
                    ret_dict["Transport"]['Highway fees']=cost_of_transport_highway_fee
                    ret_dict["Transport"]['cost_of_transport_on_site']=cost_of_transport_on_site
                except Exception:
                    pass
        else:
            ret_dict["Transport"]["cost_of_local_tickets"] = cost_of_transport
        ret_dict["Transport"]['Total travel cost'] = transport_total
        try:
            ret_dict["Transport"]["deviation"] = cost_of_transport_deviation
        except Exception:
            pass
        ret_dict["Transport"]["Notes"]= notes_transportation


        # accommodation
        ret_dict["Accommodation"] = {}
        ret_dict["Accommodation"]["deviation"] = cost_of_accommodation_deviation

        ret_dict["Accommodation"]["accommodation_cost"] = cost_of_accommodation_deviation
        ret_dict["Accommodation"]["Notes"]=notes_accommodation

        #todo finish this function

        ret_dict["Food_drinks"] = {}
        ret_dict["Food_drinks"]["Cost_food"] = cost_of_food
        ret_dict["Food_drinks"]["Cost_drinks"] = cost_of_food
        ret_dict["Food_drinks"]["deviation"] = cost_of_food_deviation
        ret_dict["Food_drinks"]["Notes"] = notes_food_drinks

        ret_dict["Activities"] = {}
        ret_dict["Activities"]["list"] = []
        for act in st.session_state["activities"]["list"]:
            ret_dict["Activities"]["list"].append(act)

        ret_dict["Activities"]["Notes"] = notes_activities
        ret_dict["Other"] = {}
        ret_dict["Other"]["addition_for_main_person"] = addition_for_bach
        ret_dict["Other"]["general_notes"] = notes_general

        return json.dumps(ret_dict)



# download_button = st.sidebar.download_button(f"Download PDF summary", data = export_pdf_data().output(dest="S").encode("latin-1"), file_name =f"{NAME}_{PARTYTYPE}_Summary.pdf")

download_button = st.sidebar.download_button(
    "Download PDF summary",
    #data = bytes(export_pdf_data().output(dest="S")),
    data = bytes(export_pdf_data().output()),
    file_name = f"{NAME}_{PARTYTYPE}_Summary.pdf"
)

download_button_json = st.sidebar.download_button(f"Download JSON data (for upload)", data = export_json_data().encode("utf-8"), file_name =f"{NAME}_{PARTYTYPE}_data.astor")

#st.button("Generate summary (experimental)",on_click=export_data)

###TESTING###


from streamlit.components.v1 import html
def open_page(url):
    open_script= """
        <script type="text/javascript">
            window.open('%s', '_blank').focus();
        </script>
    """ % (url)
    html(open_script)


# if download_button:
#     st.balloons()

#st.button("Generate summary (experimental)",on_click=open_page(export_data()))
#generate_summary_btn = st.button("Generate summary PDF(experimental)",on_click=export_data)
#if generate_summary_btn:

#    st.markdown(export_data(), unsafe_allow_html=True)
#    st.markdown(f"<script>"
#                f'var x = {export_data()[0]};'
#                f'x.click()'
#                f"</script>",unsafe_allow_html=True)

#st.download_button(label="download", data = "")


st.markdown("""
<style>
.footerstyle{
    font-size:12px !important;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)



st.markdown(
     f'<p class="footerstyle"><br>Made by: Astor Beon - v. {VERSION} - maciej.konstanty.lachowicz@gmail.com</p>',
     unsafe_allow_html=True)

