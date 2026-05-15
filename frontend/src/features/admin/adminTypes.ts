/** Admin 會員列表單筆資料。 */
export interface AdminMemberItem {
  id: number;
  email: string;
  display_name: string;
  is_admin: boolean;
  created_at: string;
}

/** Admin 會員列表回應資料。 */
export interface AdminMemberListData {
  items: AdminMemberItem[];
  page: number;
  page_size: number;
  total: number;
}
