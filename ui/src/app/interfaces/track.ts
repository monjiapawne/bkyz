export interface Track {
    id: number;
    position: number;
    total: number;
    unit: string;
    medium: string;
    book_id: number;
    active: boolean;
    notes: string | null;
}