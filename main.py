import random
import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image

#image = Image.open('dominik_cut.png')


transport_min=-1
transport_max=1
accom_min=-1
accom_max=-1
foods_min = -1
foods_max=-1
NAME = "Maja"
PARTYTYPE = "Bachelor"

st.set_page_config(page_title=f"{NAME}'s {PARTYTYPE} Party - cost breakdown calculator",layout="wide")#, page_icon = st.image(image))


if 'activities' not in st.session_state:
    st.session_state['activities'] = [("Paintball",150)]
    st.session_state['activities_objs'] = []

if "is_new_activity_open" not in st.session_state:
    st.session_state['is_new_activity_open']=False

random_activities=["Washing my car","Doing pushups","Drinking liquids on first sight","Trying to lick own elbow",
                   "Petting dogs","Speedrunning blood donations","Watching cartoons","Digging tunnel to China","Cracking"
                                                                                                               "joints"]

#st.set_page_config(layout="wide")
st.title(f"{NAME}'s {PARTYTYPE} party - Cost breakdown")
limit= st.number_input('Amount to be spent (initial assumption)', 600)
st.subheader('Transportation')


option = st.selectbox(
     'How will we travel?',
     ('Train', 'Car','No travel - staying in city'))
trans_col1, trans_col2 = st.columns(2)
if(option == "Train"):

    with trans_col1:
        cost_of_transport = st.number_input('Cost of the ticket (two ways)', 150)
    with trans_col2:
        cost_of_transport_on_site= st.number_input('Cost of transportation on site', 20)
    transport_total = int(cost_of_transport) + int(cost_of_transport_on_site)
elif option == 'No travel - staying in city':
    cost_of_transport = st.text_input('Cost of local tickets', '10')
else:
    adv = st.checkbox('Advanced transport calculations')
    if not adv:
        with trans_col1:
            cost_of_transport_fuel = st.text_input('Cost of fuel:', '250')
        with trans_col2:
            cost_of_transport_on_site = st.text_input('Cost of transportation on site', '20')
        transport_total = int(cost_of_transport_fuel) + int(cost_of_transport_on_site)
    else:
        #Advanced cost calculating for car
        with trans_col1:
            cost_of_transport_litres_per_100km = st.number_input('Litres of fuel 100km:', 10)
            cost_of_transport_cost_of_litre = st.number_input("Cost of single litre:", 7)
            cost_of_transport_length = st.number_input('Length of whole route(km) - two ways:', 356)
        with trans_col2:
            cost_of_transport_highway_fee = st.number_input('Cost of highway fees:', 20)
            cost_of_transport_on_site = st.number_input('Cost of transportation on site', 20)

        transport_total = float(cost_of_transport_highway_fee) + \
                          float(cost_of_transport_length) / 100 * float(cost_of_transport_cost_of_litre) *\
                          float(cost_of_transport_litres_per_100km) + float(cost_of_transport_on_site)

        cost_of_transport_deviation = st.number_input('Deviation/Reserve (%):', 10)
        cost_of_transport_deviation_calculation = transport_total/int(cost_of_transport_deviation)
        st.markdown("""
        <style>
        .big-font {
            font-size:20px !important;
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown(f'<p class="big-font">Including {cost_of_transport_deviation}% deviation, total cost of transport is: ---> {transport_total + transport_total/float(cost_of_transport_deviation)}</p>', unsafe_allow_html=True)
notes_transportation = st.text_input("Notes for transportation: ","None")
st.subheader('Accomodation')
acom_col1, acom_col2 = st.columns(2)
with acom_col1:
    cost_of_accomodation = st.number_input('Cost of accomodation(total):', 220)
with acom_col2:
    cost_of_accomodation_deviation = st.number_input('Deviation/Reserve(%):', 5)
st.markdown("""
<style>
.big-font {
    font-size:20px !important;
}
</style>
""", unsafe_allow_html=True)
try:
    accomodation_total_deviation_calculation =int(cost_of_accomodation) / float(cost_of_accomodation_deviation)
    accom_min=int(cost_of_accomodation)-accomodation_total_deviation_calculation
    accom_max=int(cost_of_accomodation)+accomodation_total_deviation_calculation
except Exception:
    accomodation_total_deviation_calculation=0
    accom_min,accom_max=int(cost_of_accomodation),int(cost_of_accomodation)
if accomodation_total_deviation_calculation==0:
    st.markdown(
        f'<p class="big-font">Total cost of transport is: ---> {cost_of_accomodation}</p>',
        unsafe_allow_html=True)
else:
    st.markdown(
        f'<p class="big-font">Including {cost_of_accomodation_deviation}% deviation, total cost of transport is between : ---> {int(cost_of_accomodation)-accomodation_total_deviation_calculation} and {int(cost_of_accomodation)+accomodation_total_deviation_calculation}</p>',
        unsafe_allow_html=True)

notes_accomodation = st.text_input("Notes for accomodation: ","None")
st.subheader('Food & Drinks')
food_col1, food_col2 = st.columns(2)
with food_col1:
    cost_of_food = st.number_input('Cost of food', 160)
with food_col2:
    cost_of_drinks = st.number_input('Cost of drinks (alc)', 160)
total_cost_foods_drinks = int(cost_of_food) + int(cost_of_drinks)
cost_of_food_deviation = st.number_input('Deviation:', 0)

try:
    foods_total_deviation_calculation =int(total_cost_foods_drinks) / float(cost_of_food_deviation)
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

notes_transportation = st.text_input("Notes for foods & drinks: ","None")

st.subheader("Activities")

def generate_knowledge_summary():
    pass
count=0
initial = True

def delete_from_activities(index):
    if initial:

        return
    del st. session_state['activities'][index]




for key,val in st.session_state['activities']:
    col_1, col_2 = st.columns(2)
    with col_1:
        x = st.number_input(key,val)
    st.session_state['activities_objs'].append(x)
    st.session_state['activities'][count]=(key,x)
    #st.button(f"DELETE - {key.split(' ')[0]}",on_click=delete_from_activities)

    with col_2:
        st.text("   ")
        st.text("   ")
        st.button(f"""DELETE -\n {key}""",on_click=delete_from_activities,args=(count,))
    count+=1
notes_activities = st.text_input("Notes for activities","None")

def add_activity_panel():
    st.session_state['is_new_activity_open']=True

if (st.session_state['is_new_activity_open']):
    if "temp new activity" not in st.session_state:
        st.session_state["temp new activity"]=random.choice(random_activities)
    act_name = st.text_input(f"New activity name: ",st.session_state["temp new activity"],)

    def add_activity():
        st.write(act_name)
        if act_name:
            st.write(act_name)
        st.session_state['activities'].append((act_name,0))
        #####st.session_state['activities_objs'].append(act_name)
        st.session_state['is_new_activity_open'] = False


    st.button("Approve new activity",on_click=add_activity)
st.button("Add new activity",on_click=add_activity_panel)

notes_transportation = st.text_input("Notes for activities: ","None")
initial=False

activities_cost = sum([int(x[1]) for x in st.session_state['activities']])

total_cost = transport_total + activities_cost+int(cost_of_accomodation) + total_cost_foods_drinks

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

    knowledge_summary+=f"Accomodation -> "
    if accomodation_total_deviation_calculation !=0:
        accom_min = int(cost_of_accomodation)-accomodation_total_deviation_calculation
        accom_max=int(cost_of_accomodation)+accomodation_total_deviation_calculation
        knowledge_summary+=f"{accom_min} <-> {accom_max}<br>"
    else:
        knowledge_summary+=f"{cost_of_accomodation}<br>"

    knowledge_summary+=f"Foods & drinks -> "
    if(foods_total_deviation_calculation!=0):
        foods_min = total_cost_foods_drinks-foods_total_deviation_calculation
        foods_max = total_cost_foods_drinks+foods_total_deviation_calculation
        knowledge_summary+=f"{foods_min} <-> {foods_max}<br>"
    else:
        knowledge_summary+=f"{total_cost_foods_drinks}<br>"

    knowledge_summary+=f"Activities -> {activities_cost}:<br>"
    for activity in st.session_state['activities']:
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
true_total_cost = transport_total + int(cost_of_accomodation) + total_cost_foods_drinks+activities_cost
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

notes_general = st.text_input("General notes for whole party: ","None")


def create_download_link(val, filename):
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.pdf">Click here to download summary (experimental)</a>'


def export_data():
    st.balloons()

    pdf = FPDF('P', 'mm', 'A4')
    pdf.add_page()
    pdf.set_font('Arial', 'B', 25)
    pdf.cell(190, 10, f'{NAME}\'s party cost breakdown.', 0, 1, 'C')
    pdf.set_font('Arial', 'B', 15)
    pdf.ln(5)
    pdf.cell(40, 10, f'Transport: {option}', 0, 1)
    pdf.set_font('Arial', '', 12)

    if "No travel" not in option:
        if option == "Train":
            pdf.cell(70, 10, f'Cost of ticket (two ways): {cost_of_transport}', 0, 1)
            pdf.cell(70, 10, f'Cost of transport on site: {cost_of_transport_on_site}', 0, 1)
        else:
            if not adv:
                pdf.cell(70, 10, f'Cost of fuel (two ways): {cost_of_transport_fuel}', 0, 1)
                pdf.cell(70, 10, f'Cost of transport on site: {cost_of_transport_on_site}', 0, 1)
            else:
                pdf.cell(70, 10, f'Liters per 100km: {cost_of_transport_litres_per_100km}', 0, 1)
                pdf.cell(70, 10, f'Cost of single liter: {cost_of_transport_cost_of_litre}', 0, 1)
                pdf.cell(70, 10, f'Distance to drive: {cost_of_transport_length}', 0, 1)
                pdf.cell(70, 10, f'Highway fees: {cost_of_transport_highway_fee}', 0, 1)
                pdf.cell(70, 10, f'Cost of transport on site: {cost_of_transport_on_site}', 0, 1)


        pdf.cell(70, 10, f'Total travel cost: {transport_total}', 0, 1)
        pdf.cell(70, 10, f"Notes: {notes_transportation}",0,1)
        pdf.ln(5)

        #Accomodation
        pdf.set_font('Arial', 'B', 15)
        #todo continue here - finish the report
        pdf.cell(40, 10, f'Accomodation:', 0, 1)
        pdf.set_font('Arial', '', 12)
        pdf.cell(70, 10, f'Total cost of accomodation: {cost_of_accomodation*(1-cost_of_accomodation_deviation)}-{cost_of_accomodation*(1+cost_of_accomodation_deviation)}', 0, 1)
        pdf.cell(70, 10, f'Accomodation cost deviation: {cost_of_accomodation_deviation}%', 0, 1)
        pdf.cell(40, 10, f'Notes: {notes_accomodation}', 0, 1)
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 15)
        pdf.cell(40, 10, f'Foods & drinks:', 0, 1, 'C')
        pdf.set_font('Arial', '', 12)
        pdf.cell(70, 10, f"Cost of food: {cost_of_food}", 0, 1)
        pdf.cell(70, 10, f"Cost of food: {cost_of_drinks}", 0, 1)
        pdf.cell(70, 10, f"Total cost of f&d: {(cost_of_drinks+cost_of_food)*(1-cost_of_food_deviation)} - {(cost_of_drinks+cost_of_food)*(1-cost_of_food_deviation)}", 0, 1)
        pdf.cell(70, 10, f"Deviation of cost of food and drinks: {cost_of_food_deviation}%", 0, 1)

        pdf.ln(5)
        pdf.set_font('Arial', 'B', 15)
        pdf.cell(40, 10, f'Activities:', 0, 1)
        pdf.set_font('Arial', '', 12)
        #for act, actobj in zip(st.session_state["activities"],st.session_state["activities_objs"]):
        for act in st.session_state["activities"]:
            pdf.cell(70, 10, f"{act[0]}: {act[1]}", 0, 1)

        pdf.cell(70, 10, f"Notes: {notes_activities}", 0, 1)
        pdf.ln(10)
        pdf.set_font('Arial', 'B', 15)
        pdf.cell(40, 10, f'Total cost (including deviations and general additional cost',0,1)
        pdf.cell(40,10,f'of the main person - {addition_for_bach}) is:'
                         f'{round(min_costs,2)} - {round(max_costs,2)}', 0, 1)
        pdf.set_font('Arial', '', 12)
        pdf.cell(70, 10, f"General notes: {notes_general}", 0, 1)
    html = create_download_link(pdf.output(dest="S").encode("latin-1"), "test")
    return html
    #st.markdown({html}, unsafe_allow_html=True)
    #st.button("Experimental", on_click=lambda x: html.cl)



#st.button("Generate summary (experimental)",on_click=export_data)

###TESTING###
from fpdf import FPDF
import base64
from tempfile import NamedTemporaryFile

from streamlit.components.v1 import html
def open_page(url):
    open_script= """
        <script type="text/javascript">
            window.open('%s', '_blank').focus();
        </script>
    """ % (url)
    html(open_script)

#st.button("Generate summary (experimental)",on_click=open_page(export_data()))
generate_summary_btn = st.button("Generate summary PDF(experimental)",on_click=export_data)
if generate_summary_btn:

    st.markdown(export_data(), unsafe_allow_html=True)
    st.markdown(f"<script>"
                f'var x = {export_data()};'
                f'x.click()'
                f"</script>",unsafe_allow_html=True)

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
     f'<p class="footerstyle"><br>Made by: Astor Beon - v. 1.3</p>',
     unsafe_allow_html=True)



