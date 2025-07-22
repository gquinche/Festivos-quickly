import holidays
import streamlit as st

# do a chart with the holidays in Colombia

def main():
    st.title("Holidays in Colombia")
    
    # Create a holidays object for Colombia
    col_holidays = holidays.country_holidays("CO", years=2025)


    # Get the list of holidays
    holiday_list = [(date, name) for date, name in col_holidays.items()]

    # Display the holidays in a table
    st.write("### List of Holidays in Colombia")
    st.table(holiday_list)

from datetime import date

def get_holiday_summary(country,year,include_previous_5=True, include_next_5=True,only_working_days=True):
    """Get a summary of holidays for a given country and year."""
    start_year = year - 5 if include_previous_5 else year
    end_year = year + 5 if include_next_5 else year
    holidays_obj = holidays.country_holidays(country, years=range(start_year, end_year + 1))
    # create working_days_holidays by filtering those that don't fall on weekends
    working_days_holidays = {date: name for date, name in holidays_obj.items()
                                if date.weekday() < 5 or not only_working_days}  # Monday to Friday are working days
    count_per_year = {}
    for date, name in working_days_holidays.items():
        year = date.year
        if year not in count_per_year:
            count_per_year[year] = 0
        count_per_year[year] += 1
    return count_per_year
import pandas as pd

# import something to map ISO country codes to country names

import pycountry

def get_country_comparison(countries,year=2025, include_previous_5=True, include_next_5=True, only_working_days=True):
    """Get a comparison of holidays for multiple countries."""
    country_holiday_counts = {}
    for country in countries:
        country_holiday_counts[country] = get_holiday_summary(country, year, include_previous_5, include_next_5)
    return country_holiday_counts


if __name__ == "__main__":
    st.set_page_config(page_title="Colombia Holidays", layout="wide")
    all_countries_names_and_iso = [(country.name, country.alpha_2) for country in pycountry.countries]
    default_countries = ["Colombia", "United States", "Chile", "Mexico", "Brazil", "Costa Rica"]
    selected_countries = st.multiselect(
        "Select countries to compare holiday counts",
        options=[name for name, iso in all_countries_names_and_iso],
        default=default_countries
    )
    # use holiday_counts for each country to build a line_chart merging all of them
    countries_holiday_counts = {}
    iso_countries = [country.alpha_2 for country in pycountry.countries if country.name in selected_countries]
    countries_real_holiday_counts = get_country_comparison(iso_countries, year=2025,
                                                       include_previous_5=True, include_next_5=True,
                                                       only_working_days=True)
    
    countries_holiday_counts = get_country_comparison(iso_countries, year=2025,
                                                       include_previous_5=True, include_next_5=True)

    # Merge all holiday counts into a single DataFrame for plotting
    # display dataframe
    st.write("### Holiday Counts by Country")

    st.line_chart(countries_holiday_counts, use_container_width=True,width=800, height=400,x_label="Year")
    st.scatter_chart(countries_holiday_counts, use_container_width=True,width=800, height=400,x_label="Year")

    st.write("### Free working day holidays by Country")
    st.markdown("This table shows the number of holidays per year for each selected country, we only consider holidays that fall on working days (Monday to Friday).")

    st.line_chart(countries_real_holiday_counts, use_container_width=True,width=800, height=400,x_label="Year")
    st.scatter_chart(countries_real_holiday_counts, use_container_width=True,width=800, height=400,x_label="Year")

    # show the delta between the two charts
    st.write("### Difference between total holidays and working day holidays")
    # create subtraction of the two dataframes
    delta_holidays = pd.DataFrame(countries_holiday_counts) - pd.DataFrame(countries_real_holiday_counts)
    st.line_chart(delta_holidays, use_container_width=True,width=800, height=400,x_label="Year")


    main()