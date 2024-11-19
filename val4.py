import pandas as pd
import streamlit as st

# Initialize session state for navigation and validations
if "validations" not in st.session_state:
    st.session_state.validations = []

if "current_index" not in st.session_state:
    st.session_state.current_index = 0

if "validation_started" not in st.session_state:
    st.session_state.validation_started = False


def main_page():
    """Main page for file upload and starting validation."""
    st.title("Valida las Cadenas asignadas a los restaurantes")

    # File upload
    uploaded_file = st.file_uploader(
        "Sube tu archivo (Excel o CSV)", type=["xlsx", "csv", "xls"])

    if uploaded_file:
        # Store the uploaded file name in session state
        st.session_state.df_name = uploaded_file.name

        # Determine the file type and load the DataFrame
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(".xlsx") or uploaded_file.name.endswith(".xls"):
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Tipo de archivo no soportado.")
            return

        # Drop 'Unnamed: 0' column if it exists
        if 'Unnamed: 0' in df.columns:
            df = df.drop(columns=['Unnamed: 0'])

        # Show the first few rows of the DataFrame
        st.write("### Vista previa de los datos:")
        st.dataframe(df.head())

        # Add a button to start validation
        if st.button("Comenzar"):
            st.session_state.validation_started = True
            st.session_state.df = df  # Save DataFrame in session state


def validation_page():
    """Validation page for processing row-by-row."""
    st.title("Proceso de Validación")

    df = st.session_state.df  # Retrieve the stored DataFrame

    # Initialize validations if this is the first load
    if not st.session_state.validations or len(st.session_state.validations) != len(df):
        st.session_state.validations = ["No revisado"] * len(df)

    # Current row details
    current_index = st.session_state.current_index
    row = df.iloc[current_index]

    # Display row details
    st.write(f"### Validando fila {current_index + 1} de {len(df)}")
    st.write("---")

    # Use columns for a neat layout
    col1, col2 = st.columns([1, 2])

    # Key details on the left
    with col1:
        st.markdown(f"**Nombre Restaurante:**")
        st.info(row["cluster_name_clean"])

        st.markdown(f"**Cadena Asignada:**")
        st.info(row["normalized_main_chain"])

    # Additional details on the right
    with col2:
        st.markdown("**Otros Detalles:**")
        excluded_columns = ['cluster_name_clean', 'normalized_main_chain']
        for column, value in row.items():
            if column not in excluded_columns:
                st.markdown(f"- **{column}:** {value}")

    st.write("---")

    # Validation buttons
    # Validation buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Correcto", key="boton_correcto"):
            st.session_state.validations[current_index] = "Correcto"
            if current_index < len(df) - 1:
                st.session_state.current_index += 1
                st.rerun()  # Updated from st.experimental_rerun()
    with col2:
        if st.button("Incorrecto", key="boton_incorrecto"):
            st.session_state.validations[current_index] = "Incorrecto"
            if current_index < len(df) - 1:
                st.session_state.current_index += 1
                st.rerun()  # Updated from st.experimental_rerun()
    with col3:
        if st.button("Atras", key="boton_atras") and current_index > 0:
            st.session_state.current_index -= 1
            st.rerun()  # Updated from st.experimental_rerun()

    # Save results button
    if st.button("Guardar Validación"):
        df["Validación"] = st.session_state.validations

        # Get the original filename
        original_filename = st.session_state.df_name

        # Determine the file extension and create the new filename
        if original_filename.endswith(".csv"):
            validated_file_name = original_filename.replace(
                ".csv", "_validacion.csv")
            df.to_csv(validated_file_name, index=False)
        elif original_filename.endswith((".xlsx", ".xls")):
            validated_file_name = original_filename.replace(
                ".xlsx", "_validacion.xlsx").replace(".xls", "_validacion.xls")
            df.to_excel(validated_file_name, index=False)
        else:
            st.error("Formato de archivo no soportado para guardar.")
            return

        st.success(f"La validación fue guardada exitosamente en: {
                   validated_file_name}.")


if st.session_state.validation_started:
    validation_page()
else:
    main_page()


#        streamlit run val4.py
