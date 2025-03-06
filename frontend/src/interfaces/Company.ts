export interface Company {
  new: { [key: string]: [[string, string, boolean]] };
  removed: { [key: string]: [[string, string, boolean]] };
}

export interface ChangesJsonData {
  new_date: string;
  previous_date: string;
  sofi: Company;
  galileo: Company;
}
