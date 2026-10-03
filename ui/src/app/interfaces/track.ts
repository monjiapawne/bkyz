export interface Track {
    id: number;
    position: number;
    total: number;
    unit: string;
    medium: string;
    book_id: number;
    active: boolean;
    notes: string | null;
    position_updated_at: string | null;
    rating: number | null;
    sort_order: number;
}