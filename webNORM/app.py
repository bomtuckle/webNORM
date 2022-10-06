import streamlit as st
import functions

st.set_page_config(layout='wide')


def cipw():
    st.write('# webNORM')
    st.write("""
        A web app to calculate normative mineralogy from bulk geochemistry data. \n
            """
             )
    
    st.write('## How To Use')
    st.write('''
    
    Your sample data must contain the 11 major oxides as a minimum, with major oxides given in weight %, and minor/trace elements in ppm. The data must be a csv or xlsx file and must have the 11 major oxides as the column names in the first row.
    Column names must contain only the oxide/trace name and nothing else i.e. "SiO2" not "SiO2_pct". \n

    1. Upload the data and check that everthing looks ok \n

    2. Choose your Fe Correction method:
        - "Le Maitre" uses the method set out by Le Maitre (1976). Choose either "Volcanic" or "Plutonic" depending on your samples
        - "Constant" allows you to select a set value
        - "Specified" allows you to select a column from your data that contains a correction factor \n

    3. Hit "Calculate Mineralogy!" \n
    
    ''')
    st.markdown(functions.download_template(), unsafe_allow_html=True)

    # Sidebar upload file
    st.sidebar.write('## Data Upload')
    st.sidebar.write(
        """
        Upload your bulk geochemisty sample data below. 
        """
            )
    

   


    file = st.sidebar.file_uploader(' ', type=['.csv', '.xlsx'])

    data = functions.load_data(file)

    if file is not None:
        sum_threshold=90
        data['Sum'] = functions.major_sum(data)
        st.write(
            data.style.apply(
                functions.highlight_lessthan, threshold=sum_threshold, column='Sum', axis=1
            )
        )
        n_samples = functions.summation_warning(data, sum_threshold)
        if n_samples > 0:
            st.write("""
            **Warning!** {} samples sum up to less than {}%. The highlighted cells show these samples. *These samples may give unexpected results* \n
            """.format(n_samples, sum_threshold)
            )



    st.sidebar.write('## Fe Correction Method')
    fe_option = st.sidebar.selectbox('Fe Correction Method', ['None', 'Constant', 'Le Maitre', 'Specified'])

    if fe_option == 'None':
        rock_select = None

    if fe_option == 'Constant':
        fe_slider = st.sidebar.slider(label='Correction Factor', min_value=0.0, max_value=1.0, step=0.01)
        rock_select = None


    elif fe_option == 'Specified':
        if file is not None:
            specified_ops = data.columns.tolist()
            chosen_col = st.sidebar.selectbox('Choose Column', specified_ops)
            rock_select = None


    elif fe_option == 'Le Maitre':
        rock_select = st.sidebar.radio(label='Igneous Type', options=['Plutonic', 'Volcanic'])
        # remove capitilisation
        if rock_select == 'Plutonic':
            rock_select = 'plutonic'
        
        elif rock_select == 'Volcanic':
            rock_select = 'volcanic'
        
        else:
            rock_select = None

    st.sidebar.write('### Calculate')
    cal_button = st.sidebar.empty()

    if file is not None:
        if cal_button.button('Calculate Mineralogy!'):
            if fe_option == 'None':
                adj_factor = None

            if fe_option == 'Constant':
                corrected = functions.fe_correction(df=data, constant=fe_slider)
                data['FeO'] = corrected['FeO']
                data['Fe2O3'] = corrected['Fe2O3']
                adj_factor = None


            elif fe_option == 'Specified':
                corrected = functions.fe_correction(df=data, constant=data[chosen_col])
                data['FeO'] = corrected['FeO']
                data['Fe2O3'] = corrected['Fe2O3']
                adj_factor = None


            elif fe_option == 'Le Maitre':
                adj_factor = None

        
            
            norms = functions.calculate_norms(df=data, fe_correction_method=fe_option, fe_correction_type=rock_select, fe_constant=adj_factor)
            
            st.write(norms.style.apply(functions.highlight_greaterthan, threshold=101, column='Sum', axis=1))
            
            if len(norms[norms['Sum'] > 100.1]):
                st.write('*Highlighted cells show where the normative sum is > 100.1%*')
            st.markdown(functions.download_df(norms), unsafe_allow_html=True)



    # Contact


    # Reference
    st.write('### References')
    st.write('''
    Le Maitre, R.W. Some problems of the projection of chemical data into mineralogical classifications
        *Contr. Mineral. and Petrol. 56, 181–189 (1976).* https://doi.org/10.1007/BF00399603
        
    Verma, S.P., Torres-Alvarado, I.S. & Velasco-Tapia, F., 2003. A revised CIPW norm.
    *Schweizerische Mineralogische und Petrographische Mitteilungen, 83(2), pp.197–216.* http://doi.org/10.5169/seals-63145
    ''')


cipw()
