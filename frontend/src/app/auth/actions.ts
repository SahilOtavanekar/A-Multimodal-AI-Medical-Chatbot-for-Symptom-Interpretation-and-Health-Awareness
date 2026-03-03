'use server'

import { revalidatePath } from 'next/cache'
import { redirect } from 'next/navigation'
import { createClient } from '@/utils/supabase/server'
import { headers } from 'next/headers'

export async function login(formData: FormData) {
    const supabase = await createClient()

    const data = {
        email: formData.get('email') as string,
        password: formData.get('password') as string,
    }

    const { error } = await supabase.auth.signInWithPassword(data)

    if (error) {
        redirect('/auth?error=true&message=' + encodeURIComponent(error.message))
    }

    revalidatePath('/', 'layout')
    redirect('/chat')
}

export async function signup(formData: FormData) {
    const supabase = await createClient()

    const data = {
        email: formData.get('email') as string,
        password: formData.get('password') as string,
    }

    const headerStore = await headers()
    const origin = headerStore.get('origin') || 'http://localhost:3000'

    const { data: signUpData, error } = await supabase.auth.signUp({
        ...data,
        options: {
            emailRedirectTo: `${origin}/auth/callback`,
        }
    })

    if (error) {
        redirect('/auth?error=true&message=' + encodeURIComponent(error.message))
    }

    // Check if the user needs to confirm their email
    if (signUpData.user && !signUpData.session) {
        redirect('/auth?error=false&message=' + encodeURIComponent('Please check your email to verify your account.'))
    }

    revalidatePath('/', 'layout')
    redirect('/chat')
}
