import { createClient } from '@/utils/supabase/server'
import { NextResponse } from 'next/server'

export async function POST(request: Request) {
    const supabase = await createClient()

    // Sign out the user
    await supabase.auth.signOut()

    // Redirect to the landing page
    const url = new URL('/', request.url)
    return NextResponse.redirect(url)
}
