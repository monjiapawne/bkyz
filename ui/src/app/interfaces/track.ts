export interface Track {
    id: number;
    position: number;
    total: number;
    unit: string;
    medium: string;
    book_id: number;
    active: boolean;
    notes: string | null;
    last_read_at: string | null;
    rating: number | null;
    sort_order: number;
}