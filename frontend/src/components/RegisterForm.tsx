export function RegisterForm() {
    return(
        <form className="bg-[#f0dcdb] fixed inset-0 m-auto h-fit w-fit grid gap-3 p-18 outline-2 rounded-2xl shadow-2xl">

        <h1 className="text-5xl font-bold mb-8 m-auto">Register</h1>
        <input
            className="bg-[#e4cfce] flex-1 rounded-lg px-2 py-2 outline-none transition-all duration-200 focus-visible:ring-2 focus-visible:ring-[#543937]"
            placeholder="Username"
        />
        <hr className="border-[#6647455b] mt-2 mb-2 outline-0 w-70"/>
        <input
            className="bg-[#e4cfce] flex-1 rounded-lg px-2 py-2 outline-none transition-all duration-200 focus-visible:ring-2 focus-visible:ring-[#543937]"
            placeholder="Password"
            type="password"
        />
        <input 
            className="bg-[#e4cfce] flex-1 rounded-lg px-2 py-2 outline-none transition-all duration-200 focus-visible:ring-2 focus-visible:ring-[#543937]"
            placeholder="Confirm Password"
            type="password"
        />
        <button className="bg-[#664745] text-[#EDCCCA] font-bold w-32 rounded-lg mt-8 m-auto">Register</button>
        <button className="font-semibold m-auto pt-2">Sign in</button>

      </form>
    )
}