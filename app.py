import streamlit as st
import pandas as pd
import io

# Define the main function for the Streamlit app
def main():
    st.title('Lift Generator App')

    # File upload
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    
    # File is uploaded
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, keep_default_na=False)
        st.success(f'File {uploaded_file.name} loaded successfully.')
        
        # Display the DataFrame
        st.write("### CSV File Preview")
        st.dataframe(df.head())

        # Input fields for user
        subblocks_input = st.text_input('Enter numbers of Subblocks for block types:')
        code_input = st.text_input('Enter Subblock Codes:')

        if st.button('Generate Lift'):
            try:
                if df.empty:
                    st.error('Please upload a CSV file first.')
                else:
                    # Process the data
                    df_temp = df.copy()
                    df_temp = df_temp[["Name", "Link", "Category", "Extremety"]]
                    
                    all_unique_codes = df_temp[df_temp.columns[-1:]].to_numpy()
                    all_unique_codes = set([item for row in all_unique_codes for item in row])

                    blocks = [int(x) for x in list(subblocks_input)]
                    code = list(code_input)

                    if sum(blocks) != len(code):
                        st.error('The code entered is either too long or short for the number of blocks.')
                    elif any(c not in all_unique_codes for c in code):
                        st.error('Invalid character code.')
                    else:
                        # lift = {
                        #     "S": [-1] * blocks[0],
                        #     "A": [-1] * blocks[1],
                        #     "B": [-1] * blocks[2],
                        #     "C": [-1] * blocks[3]
                        # }
                        lift = {
                            "A": [-1] * blocks[0],
                            "B": [-1] * blocks[1],
                            "C": [-1] * blocks[2]
                        }


                        curr_idx = 0
                        for block in lift:
                            for j, subblock in enumerate(lift[block]):
                                row = df_temp.sample(n=1)

                                curr_cat = block + str(j+1)
                                
                                counter = 0
                                while curr_cat not in row["Category"].iloc[0].split(",") or code[curr_idx] not in row["Extremety"].iloc[0].split(","):
                                    row = df_temp.sample(n=1)
                                    counter += 1
                                    if counter > 696:
                                        raise Exception(f"Extremety code {code[curr_idx]} not available for block {block + str(j+1)}")
                                        
                                lift[block][j] = row.index[0]
                                curr_idx += 1

                        lift_ = {}
                        for block in lift:
                            for i, exercise in enumerate(lift[block]):
                                lift_[block + str(i+1)] = df_temp.loc[exercise]

                        out = pd.DataFrame.from_dict(lift_).T.drop(columns=["Category"])
                        out["Sets/Reps"] = pd.Series(dtype='int')

                        # Display the resulting DataFrame
                        st.write("### Generated Lift")
                        st.dataframe(out)

                        # Prepare CSV for download
                        csv = out.to_csv(index_label='Exercise')
                        st.download_button(
                            label="Download Lift Data as CSV",
                            data=csv,
                            file_name='generated_lift.csv',
                            mime='text/csv'
                        )
            except Exception as e:
                st.error(f'Error: {str(e)}')

if __name__ == "__main__":
    main()
