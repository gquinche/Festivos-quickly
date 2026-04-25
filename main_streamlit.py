import holidays
import streamlit as st
import pandas as pd

# import something to map ISO country codes to country names
import pycountry

# do a chart with the holidays in Colombia
# use light theme

st.set_page_config(page_title="Holiday Explorer", layout="wide")

ip_fetcher_component = st.components.v2.component(
    "ip_fetcher",
    js="""
    let fetched = false;
    export default function({ setStateValue }) {
        if (!fetched) {
            fetched = true;
            fetch('https://api.ipify.org')
                .then(r => r.text())
                .then(ip => setStateValue("ip", ip))
                .catch(e => {
                    setStateValue("ip", "");
                });
        }
    }
    """
)

calendar_component = st.components.v2.component(
    "calendar",
    html="""
    <script src="https://cdn.jsdelivr.net/npm/fullcalendar@6.1.11/index.global.min.js"></script>
    <div id="calendar"></div>
    """,
    js="""
    export default function({ data, parentElement }) {
        const render = () => {
            const calEl = parentElement.querySelector("#calendar");
            calEl.innerHTML = '';

            // Apply Streamlit Theme
            const root = parentElement.querySelector("#calendar");
            const stStyles = window.getComputedStyle(root);

            const bgColor = stStyles.getPropertyValue('--st-background-color');
            const textColor = stStyles.getPropertyValue('--st-text-color');
            const primaryColor = stStyles.getPropertyValue('--st-primary-color');
            const borderColor = stStyles.getPropertyValue('--st-border-color') || 'var(--st-secondary-background-color)';
            const secondaryBgColor = stStyles.getPropertyValue('--st-secondary-background-color');

            if (bgColor) root.style.setProperty('--fc-page-bg-color', bgColor);
            if (textColor) {
                root.style.setProperty('--fc-text-color', textColor);
                root.style.setProperty('--fc-daygrid-event-color', textColor);
            }
            if (primaryColor) {
                root.style.setProperty('--fc-event-bg-color', primaryColor);
                root.style.setProperty('--fc-event-border-color', primaryColor);
                root.style.setProperty('--fc-button-bg-color', primaryColor);
                root.style.setProperty('--fc-button-border-color', primaryColor);
            }
            if (borderColor) {
                root.style.setProperty('--fc-border-color', borderColor);
            }
            if (secondaryBgColor) {
                root.style.setProperty('--fc-today-bg-color', secondaryBgColor);
                root.style.setProperty('--fc-button-active-bg-color', secondaryBgColor);
                root.style.setProperty('--fc-button-hover-bg-color', secondaryBgColor);
            }

            const isMobile = window.innerWidth <= 600;

            const cal = new window.FullCalendar.Calendar(calEl, {
                initialView: 'multiMonthYear',
                initialDate: data.year + '-01-01',
                headerToolbar: {
                    left: 'prev,next' + (isMobile ? '' : ' today'),
                    center: 'title',
                    right: isMobile ? 'multiMonthYear,listMonth' : 'multiMonthYear,dayGridMonth,listMonth'
                },
                buttonText: {
                    today: 'Today',
                    month: 'Month',
                    list: 'List',
                    year: 'Year',
                    multiMonthYear: 'Year',
                    dayGridMonth: 'Month',
                    listMonth: 'List'
                },
                events: data.events || [],
                height: 'auto'
            });
            cal.render();

            let lastIsMobile = isMobile;
            const resizeObserver = new ResizeObserver(entries => {
                const currentIsMobile = window.innerWidth <= 600;
                if (currentIsMobile !== lastIsMobile) {
                    lastIsMobile = currentIsMobile;
                    cal.setOption('headerToolbar', {
                        left: 'prev,next' + (currentIsMobile ? '' : ' today'),
                        center: 'title',
                        right: currentIsMobile ? 'multiMonthYear,listMonth' : 'multiMonthYear,dayGridMonth,listMonth'
                    });
                }
            });
            resizeObserver.observe(parentElement);
        };

        if (window.FullCalendar) {
            render();
        } else {
            const check = setInterval(() => {
                if (window.FullCalendar) {
                    clearInterval(check);
                    render();
                }
            }, 100);
        }
    }
    """,
    css="""
    #calendar {
        font-family: var(--st-font);
        color: var(--st-text-color);
        width: 100%;
        min-height: 600px;
    }

    @media (max-width: 600px) {
        .fc .fc-toolbar.fc-header-toolbar {
            flex-wrap: nowrap !important;
            gap: 2px !important;
            margin-bottom: 0.5em !important;
        }
        .fc .fc-toolbar-title {
            font-size: 1.1em !important;
            white-space: nowrap;
        }
        .fc .fc-button {
            padding: 0.2em 0.4em !important;
            font-size: 0.8em !important;
        }
    }

    @media (max-width: 400px) {
        .fc .fc-toolbar-title {
            font-size: 0.9em !important;
        }
        .fc .fc-button {
            padding: 0.2em 0.3em !important;
            font-size: 0.7em !important;
        }
    }
    """
)

st.title("Holiday explorer")

st.text("This app allows you to explore holidays in different countries. You can select a country to see its holidays for the current year, and compare holiday counts across multiple countries.")

from datetime import date
import urllib.request
import json

def get_inferred_country(client_ip=None):
    # 1. Try to use user IP address
    ip_addr = client_ip or st.context.ip_address
    if ip_addr:
        try:
            with urllib.request.urlopen(f"http://ip-api.com/json/{ip_addr}", timeout=2) as url:
                data = json.loads(url.read().decode())
                country_name = data.get('country')
                if country_name:
                    return country_name
        except:
            pass

    # 2. Try to fall back to browser locale
    try:
        locale = st.context.locale
        if locale and "-" in locale:
            country_iso = locale.split("-")[1].upper()
            country = pycountry.countries.get(alpha_2=country_iso)
            if country:
                return country.name
    except:
        pass

    # 3. Default fallback
    return "Colombia"

def main(country="Colombia", year=date.today().year):
    st.title(f"Holidays in {country}")

    # Create a holidays object for the selected country
    country_to_iso = {c.name: c.alpha_2 for c in pycountry.countries}
    iso_code = country_to_iso.get(country)

    if not iso_code:
        st.error(f"Could not find ISO code for {country}")
        return

    try:
        # holidays uses ISO codes for lookup
        country_holidays = holidays.country_holidays(iso_code, years=year)
    except NotImplementedError:
        st.error(f"Holiday data for {country} is currently not supported.")
        return


    # Display the holidays in a calendar view (First thing to show for the current year)
    st.write(f"### Calendar of Holidays in {country} ({year})")
    calendar_events = [
        {"title": name, "start": d.isoformat(), "allDay": True}
        for d, name in country_holidays.items()
    ]
    calendar_component(data={"events": calendar_events, "year": str(year)})

    # Get the list of holidays
    holiday_list = [(d, name) for d, name in country_holidays.items()]

    # Display the holidays in a table
    st.write(f"### List of Holidays in {country}")
    st.table(holiday_list)

def get_holiday_summary(country,year,include_previous_5=True, include_next_5=True,only_working_days=True):
    """Get a summary of holidays for a given country and year."""
    start_year = year - 5 if include_previous_5 else year
    end_year = year + 5 if include_next_5 else year
    holidays_obj = holidays.country_holidays(country, years=range(start_year, end_year + 1))
    # create working_days_holidays by filtering those that don't fall on weekends
    working_days_holidays = {date: name for date, name in holidays_obj.items()
                                if(date.weekday() < 5 or not only_working_days)}  # Monday to Friday are working days
    count_per_year = {}
    for date, name in working_days_holidays.items():
        year = date.year
        if year not in count_per_year:
            count_per_year[year] = 0
        count_per_year[year] += 1
    return count_per_year


def get_country_comparison(countries,year=2025, include_previous_5=True, include_next_5=True, only_working_days=True,give_long_names=True):
    """Get a comparison of holidays for multiple countries."""
    country_holiday_counts = {}
    for country in countries:
        country_holiday_counts[country] = get_holiday_summary(country, year, include_previous_5, include_next_5, only_working_days)

    if give_long_names:
        # Convert ISO country codes to full country names
        country_holiday_counts = {pycountry.countries.get(alpha_2=country).name: counts for country, counts in country_holiday_counts.items()}

    # return as a dataframe with the index being the years (as strings)
    df = pd.DataFrame(country_holiday_counts)
    df.index = df.index.astype(str)  # Convert index to string for better display
    return df


if __name__ == "__main__":
    ip_res = ip_fetcher_component(default={"ip": None}, on_ip_change=lambda: None)
    client_ip = ip_res.ip if ip_res else None

    all_countries_names_and_iso = [(country.name, country.alpha_2) for country in pycountry.countries]

    inferred_country = get_inferred_country(client_ip=client_ip)
    # verify inferred country is in the list
    if inferred_country not in [name for name, iso in all_countries_names_and_iso]:
        inferred_country = "Colombia"

    country_details = st.selectbox(
        "Select a country to see its holidays for the current year",
        options=[name for name, iso in all_countries_names_and_iso],
        index=all_countries_names_and_iso.index((inferred_country, pycountry.countries.get(name=inferred_country).alpha_2))
    )

    current_year = date.today().year
    main(country=country_details, year=current_year)

    st.write("---")

    default_countries = ["Colombia", "United States", "Chile", "Mexico", "Brazil", "Costa Rica"]
    selected_countries = st.multiselect(
        "Select countries to compare holiday counts",
        options=[name for name, iso in all_countries_names_and_iso],
        default=default_countries
    )
    # use holiday_counts for each country to build a line_chart merging all of them
    countries_holiday_counts = {}
    iso_countries = [country.alpha_2 for country in pycountry.countries if country.name in selected_countries]
    countries_real_holiday_counts = get_country_comparison(iso_countries, year=current_year,
                                                       include_previous_5=True, include_next_5=True,
                                                       only_working_days=False)
    
    countries_holiday_counts = get_country_comparison(iso_countries, year=current_year,
                                                       include_previous_5=True, include_next_5=True,
                                                       only_working_days=True)

    # Merge all holiday counts into a single DataFrame for plotting
    # display dataframe
    st.write("### Holiday Counts by Country")

    st.line_chart(countries_holiday_counts, use_container_width=True,width=800, height=400,x_label="Year")

    st.write("### Free working day holidays by Country")
    st.markdown("This table shows the number of holidays per year for each selected country, we only consider holidays that fall on working days (Monday to Friday).")

    st.line_chart(countries_real_holiday_counts, use_container_width=True,width=800, height=400,x_label="Year")

    # show the delta between the two charts
    st.write("### Difference between total holidays and working day holidays")
    # create subtraction of the two dataframes
    delta_holidays =  pd.DataFrame(countries_real_holiday_counts) - pd.DataFrame(countries_holiday_counts)
    st.bar_chart(delta_holidays, use_container_width=True,width=800, height=400,x_label="Year")