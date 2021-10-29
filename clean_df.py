def clean_df(df):
    # data cleaning
    df = (
        df
        .clean_names() # remove spacing and capitalization
        .drop(columns=['first_name', 'last_name', 'email_address']) # drop for privacy
        .dropna(subset=['company', 'position']) # drop missing values in company and position
        .to_datetime('connected_on', format='%d %b %Y')
        .filter_string(column_name='company',
                         search_string='freelance|self-employed',
                         complement=True)
    )
    return df