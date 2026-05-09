import { createClient } from '@supabase/supabase-js'

const supabaseUrl = process.env.REACT_APP_SUPABASE_URL_eklenecek_suan_database_problemi_var
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY_eklenecek_suan_database_problemi_var

export const supabase = createClient(supabaseUrl, supabaseAnonKey)