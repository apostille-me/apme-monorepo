fn main() {
    if let Err(error) = apme_catalog::validate() {
        eprintln!("invalid service catalog: {error}");
        std::process::exit(2);
    }
    println!("organization={}", apme_catalog::ORGANIZATION);
    for service in apme_catalog::SERVICES { println!("service={service}"); }
}
