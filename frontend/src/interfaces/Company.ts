export interface Company {
    new : {[key: string]: string[]};
    removed: {[key: string]: string[]};
}

export interface ChangesJsonData {
    new_date: string;
    previous_date: string;
    sofi: Company;
    galileo: Company;
}