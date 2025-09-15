-- Schema pour stocker les analyses automatiques des conversations
-- Tables pour résumés, entreprises et prénoms extraits par IA

-- Table principale pour stocker les analyses de conversations
CREATE TABLE IF NOT EXISTS conversation_analysis (
    id SERIAL PRIMARY KEY,
    chatid UUID NOT NULL,
    
    -- Informations extraites par IA
    client_name VARCHAR(255),           -- Prénom/nom extrait
    company_name VARCHAR(255),          -- Entreprise extraite
    conversation_summary TEXT,          -- Résumé complet de la conversation
    
    -- Métadonnées
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Statistiques de la conversation
    total_messages INTEGER,
    conversation_start_date TIMESTAMP,
    conversation_end_date TIMESTAMP,
    
    -- Statut de completion
    is_completed BOOLEAN DEFAULT FALSE,
    completion_analysis TEXT,
    
    -- Contrainte d'unicité sur chatid
    UNIQUE(chatid)
);

-- Index pour optimiser les requêtes
CREATE INDEX IF NOT EXISTS idx_conversation_analysis_chatid ON conversation_analysis(chatid);
CREATE INDEX IF NOT EXISTS idx_conversation_analysis_date ON conversation_analysis(analysis_date);
CREATE INDEX IF NOT EXISTS idx_conversation_analysis_company ON conversation_analysis(company_name);

-- Table pour stocker l'historique des analyses (optionnel)
CREATE TABLE IF NOT EXISTS analysis_history (
    id SERIAL PRIMARY KEY,
    chatid UUID NOT NULL,
    analysis_type VARCHAR(50) NOT NULL, -- 'summary', 'company', 'name'
    extracted_value TEXT,
    extraction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (chatid) REFERENCES conversation_analysis(chatid) ON DELETE CASCADE
);

-- Vue pour avoir un résumé facile des conversations analysées
CREATE OR REPLACE VIEW conversations_with_analysis AS
SELECT 
    ca.chatid,
    ca.client_name,
    ca.company_name,
    LEFT(ca.conversation_summary, 200) as summary_preview,
    ca.is_completed,
    ca.total_messages,
    ca.conversation_start_date,
    ca.conversation_end_date,
    ca.analysis_date,
    CASE 
        WHEN ca.conversation_summary IS NOT NULL THEN 'Oui'
        ELSE 'Non'
    END as has_summary,
    CASE 
        WHEN ca.company_name IS NOT NULL THEN 'Oui'
        ELSE 'Non'
    END as has_company,
    CASE 
        WHEN ca.client_name IS NOT NULL THEN 'Oui'
        ELSE 'Non'
    END as has_client_name
FROM conversation_analysis ca
ORDER BY ca.conversation_end_date DESC;

-- Fonction pour mettre à jour automatiquement last_updated
CREATE OR REPLACE FUNCTION update_last_updated_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_updated = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger pour mettre à jour automatiquement last_updated
DROP TRIGGER IF EXISTS update_conversation_analysis_last_updated ON conversation_analysis;
CREATE TRIGGER update_conversation_analysis_last_updated
    BEFORE UPDATE ON conversation_analysis
    FOR EACH ROW
    EXECUTE FUNCTION update_last_updated_column();

-- Commentaires pour documentation
COMMENT ON TABLE conversation_analysis IS 'Stockage des analyses IA des conversations WhatsApp';
COMMENT ON COLUMN conversation_analysis.client_name IS 'Prénom/nom du client extrait par IA';
COMMENT ON COLUMN conversation_analysis.company_name IS 'Nom de l''entreprise extraite par IA';
COMMENT ON COLUMN conversation_analysis.conversation_summary IS 'Résumé structuré de la conversation';
COMMENT ON COLUMN conversation_analysis.is_completed IS 'Indique si la conversation s''est terminée avec un contact fourni';
